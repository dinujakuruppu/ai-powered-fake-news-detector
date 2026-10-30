
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

router = APIRouter()

FACT_CHECK_URL = (
    "https://factchecktools.googleapis.com/"
    "v1alpha1/claims:search"
)


class FactCheckRequest(BaseModel):
    query: str = Field(min_length=10, max_length=500)


@router.post("/api/fact-check")
async def check_fact_sources(payload: FactCheckRequest):

    api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Google Fact Check API key is not configured."
        )

    query = payload.query.strip()

    if len(query) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please provide a longer claim."
        )

    try:
        async with httpx.AsyncClient(
            timeout=12.0
        ) as client:

            response = await client.get(
                FACT_CHECK_URL,
                params={
                    "key": api_key,
                    "query": query,
                    "pageSize": 10,
                }
            )

            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Fact Check API request timed out."
        )

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code

        raise HTTPException(
            status_code=503 if status == 429 else 502,
            detail=(
                "Fact Check API quota exceeded."
                if status == 429
                else "Google Fact Check API request failed."
            )
        )

    except (httpx.RequestError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve fact-check results."
        )

    results = []

    for claim in data.get("claims", []):
        for review in claim.get("claimReview", []):

            review_url = review.get("url", "")

            if not review_url.startswith(
                ("https://", "http://")
            ):
                continue

            publisher = review.get("publisher") or {}

            results.append({
                "claim": claim.get("text", ""),
                "publisher": publisher.get(
                    "name", "Unknown publisher"
                ),
                "rating": review.get(
                    "textualRating", "Not specified"
                ),
                "title": review.get("title", ""),
                "url": review_url,
                "review_date": review.get(
                    "reviewDate", ""
                ),
            })

            if len(results) >= 5:
                break

        if len(results) >= 5:
            break

    return {
        "query": query,
        "status": (
            "matches_found" if results else "no_matches"
        ),
        "results": results,
        "note": (
            "These are related published fact checks. "
            "Their relevance must be reviewed manually."
        ),
    }
