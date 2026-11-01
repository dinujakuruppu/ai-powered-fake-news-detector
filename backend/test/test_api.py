
import numpy as np
import pytest
from fastapi.testclient import TestClient

import main
import url_analyzer


# Fake AI model used only during automated testing
class FakeModel:
    classes_ = np.array(["FAKE", "REAL"])

    def predict_proba(self, texts):
        return np.array([[0.20, 0.80] for _ in texts])


@pytest.fixture
def client(monkeypatch):
    # Avoid loading the real ML model in API tests
    monkeypatch.setattr(
        main.joblib,
        "load",
        lambda path: FakeModel()
    )

    with TestClient(main.app) as test_client:
        yield test_client


# Test 1: Backend health
def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


# Test 2: Valid news prediction
def test_predict_valid_news(client):
    response = client.post(
        "/api/predict",
        json={
            "text": "This is a sample news statement."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] == "REAL"
    assert data["confidence"] == 80.0
    assert data["status"] == "success"


# Test 3: Short text
def test_predict_short_text(client):
    response = client.post(
        "/api/predict",
        json={"text": "short"}
    )

    assert response.status_code == 422


# Test 4: Whitespace-only text
def test_predict_empty_text(client):
    response = client.post(
        "/api/predict",
        json={"text": "             "}
    )

    assert response.status_code == 400


# Test 5: Unsupported URL
def test_unsupported_url(client):
    response = client.post(
        "/api/analyze-url",
        json={
            "url": "https://example.com/news"
        }
    )

    assert response.status_code == 400


# Test 6: Valid URL with mocked article
def test_url_analysis(client, monkeypatch):

    async def fake_fetch_article(url):
        html = """
        <html>
          <head>
            <title>Sample News Headline</title>
          </head>
          <body>
            <article>
              <p>
                This is a sufficiently detailed sample
                article used for testing the fake news
                detection application without contacting
                an external news website.
              </p>
            </article>
          </body>
        </html>
        """
        return html.encode("utf-8")

    monkeypatch.setattr(
        url_analyzer,
        "fetch_article",
        fake_fetch_article
    )

    response = client.post(
        "/api/analyze-url",
        json={
            "url": "https://www.bbc.com/news/example"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["headline"] == "Sample News Headline"
    assert data["prediction"] == "REAL"
    assert data["status"] == "success"


# Test 7: Missing Google API key
def test_missing_factcheck_key(client, monkeypatch):
    monkeypatch.delenv(
        "GOOGLE_FACT_CHECK_API_KEY",
        raising=False
    )

    response = client.post(
        "/api/fact-check",
        json={
            "query": "This is a sample claim to verify."
        }
    )

    assert response.status_code == 503
