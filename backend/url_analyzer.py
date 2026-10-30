
import asyncio
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, HttpUrl

router = APIRouter()

ALLOWED_DOMAINS = {
    "bbc.com",
    "bbc.co.uk",
    "reuters.com",
    "apnews.com",
    "theguardian.com",
    "npr.org",
}

MAX_BYTES = 1_000_000


class URLRequest(BaseModel):
    url: HttpUrl


def is_allowed(hostname: str) -> bool:
    host = hostname.lower().rstrip(".")

    return any(
        host == domain or host.endswith("." + domain)
        for domain in ALLOWED_DOMAINS
    )


async def fetch_article(url: str) -> bytes:
    timeout = httpx.Timeout(
        connect=5.0,
        read=6.0,
        write=5.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        trust_env=False,
        headers={
            "User-Agent": "NewsResearchDemo/1.0",
            "Accept": "text/html",
        },
    ) as client:

        async with client.stream("GET", url) as response:

            if 300 <= response.status_code < 400:
                raise HTTPException(
                    status_code=400,
                    detail="Redirect detected. Use the final HTTPS article URL."
                )

            response.raise_for_status()

            content_type = response.headers.get(
                "content-type", ""
            ).lower()

            if "text/html" not in content_type:
                raise HTTPException(
                    status_code=400,
                    detail="URL did not return an HTML article."
                )

            content = bytearray()

            async for chunk in response.aiter_bytes():
                content.extend(chunk)

                if len(content) > MAX_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Article page is too large."
                    )

            return bytes(content)


@router.post("/api/analyze-url")
async def analyze_news_url(
    payload: URLRequest,
    request: Request,
):
    url = str(payload.url)
    parsed = urlsplit(url)

    try:
        valid_port = parsed.port in (None, 443)
    except ValueError:
        valid_port = False

    if (
        parsed.scheme != "https"
        or not valid_port
        or parsed.username
        or parsed.password
        or not is_allowed(parsed.hostname or "")
    ):
        raise HTTPException(
            status_code=400,
            detail="Use a supported HTTPS news article URL."
        )

    try:
        html = await asyncio.wait_for(
            fetch_article(url),
            timeout=12.0,
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="News website request timed out."
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="News website did not respond in time."
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"News website returned HTTP {exc.response.status_code}."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the news website."
        )

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("meta", property="og:title")

    if title_tag and title_tag.get("content"):
        headline = str(title_tag["content"]).strip()
    elif soup.title:
        headline = soup.title.get_text(" ", strip=True)
    else:
        headline = "Unknown headline"

    article = (
        soup.select_one("article")
        or soup.select_one("main")
        or soup
    )

    for tag in article.select(
        "script, style, nav, footer, aside"
    ):
        tag.decompose()

    paragraphs = []

    for p in article.select("p"):
        content = p.get_text(" ", strip=True)

        if len(content) >= 40:
            paragraphs.append(content)

    article_text = " ".join(paragraphs)

    if len(article_text) < 80:
        raise HTTPException(
            status_code=422,
            detail="Could not extract enough article text."
        )

    text_to_analyze = article_text[:1200]

    model = request.app.state.model

    probabilities = model.predict_proba(
        [text_to_analyze]
    )[0]

    best_index = int(probabilities.argmax())

    prediction = str(
        model.classes_[best_index]
    )

    confidence = round(
        float(probabilities[best_index]) * 100,
        2
    )

    return {
        "url": url,
        "headline": headline,
        "extracted_text": text_to_analyze,
        "prediction": prediction,
        "confidence": confidence,
        "status": "success",
        "note": (
            "Experimental AI classification only. "
            "Not a verified fact-check."
        ),
    }
