# AI-Powered Fake News Detector

A full-stack machine learning project that classifies English news statements and extracts text from supported news article URLs. It also displays model confidence and lets users search for related published fact-checks through the Google Fact Check Tools API.

> **Important:** This is an **experimental news classification and fact-check search tool**, not an automated truth-verification system. A `REAL` or `FAKE` prediction does not establish whether a claim is true. Model confidence is not the probability that a news story is true.

## Features

- **Text Analysis:** Enter an English news statement to receive a `REAL` or `FAKE` model prediction.
- **News URL Analysis:** Paste an HTTPS article URL from a supported publisher to extract article text and classify it.
- **Model Confidence:** Display the model's predicted-class probability as a percentage with a progress bar.
- **Source Verification:** Search Google Fact Check Tools for relevant fact-check reports, including publisher ratings and source links.
- **Responsive UI:** A dark-themed Next.js interface for text and URL analysis.
- **Interactive API Documentation:** Test endpoints via FastAPI Swagger UI.

### Supported URL domains

The current URL analyzer allows HTTPS article URLs from:

- BBC (`bbc.com`, `bbc.co.uk`)
- Reuters (`reuters.com`)
- AP News (`apnews.com`)
- The Guardian (`theguardian.com`)
- NPR (`npr.org`)

Some publishers may block automated requests, redirect URLs, or use page structures that cannot be extracted reliably. Live-update pages may be especially difficult to parse.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Machine learning | Scikit-learn, TF-IDF, Logistic Regression, Joblib |
| Data processing | Pandas |
| Article extraction | HTTPX, Beautiful Soup |
| Fact-check search | Google Fact Check Tools API |

## Project Structure

```text
fake-news-detector/
├── backend/
│   ├── data/
│   │   ├── train.tsv
│   │   ├── valid.tsv
│   │   └── test.tsv
│   ├── models/
│   │   └── fake_news_model.joblib   # generated after training
│   ├── .env                         # local secret; never commit
│   ├── main.py                      # FastAPI application
│   ├── train_model.py               # train + validate model
│   ├── test_model.py                # command-line test
│   ├── prediction_service.py        # predictions + confidence
│   ├── url_analyzer.py              # article URL analysis
│   └── fact_check.py                # fact-check source search
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   └── FactCheckResults.tsx
│   │   └── page.tsx
│   ├── .env.local                   # local frontend config
│   └── package.json
└── README.md
```

This tree describes the current implementation. Generated files and dependency directories are omitted for clarity.

## Requirements

- Python with virtual environment support (the project was developed using a Python 3.9 environment)
- Node.js compatible with your installed Next.js version (recent Next.js versions require Node.js 20.9 or newer)
- npm
- A Google Cloud API key with **Fact Check Tools API** enabled (only needed for Source Verification)

## Local Setup

### 1. Clone or open the project

```bash
git clone <YOUR_REPOSITORY_URL>
cd fake-news-detector
```

If you already have the project on your computer, open its existing directory instead.

### 2. Configure the Python backend

On macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "fastapi[standard]" pandas scikit-learn joblib httpx beautifulsoup4 python-dotenv
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

### 3. Prepare and train the dataset (if needed)

The model is trained using the **LIAR** dataset, which contains fact-checked, predominantly political English statements. Place `train.tsv`, `valid.tsv`, and `test.tsv` inside `backend/data/`.

Dataset and paper: [LIAR: A Benchmark Dataset for Fake News Detection](https://aclanthology.org/P17-2067/).

The training pipeline uses **TF-IDF + Logistic Regression**. It maps the dataset's labels as follows:

| Original LIAR label | Model class |
| --- | --- |
| `pants-fire`, `false`, `barely-true` | `FAKE` |
| `mostly-true`, `true` | `REAL` |
| `half-true` | Excluded from this binary training setup |

With the virtual environment active and while in the `backend` directory:

```bash
python train_model.py
```

This generates `backend/models/fake_news_model.joblib`. To test a statement in the terminal:

```bash
python test_model.py
```

**Observed validation accuracy during development: 65.54%.** This is a result on the project's LIAR validation split, **not** a reliability guarantee for current news, general articles, or unseen topics. The model should also be evaluated separately on `test.tsv` before making broader performance claims.

### 4. Configure the Google Fact Check API key

Enable the **Fact Check Tools API** in [Google Cloud Console](https://console.cloud.google.com/apis/library). Create a key and restrict it to that API where possible.

Create `backend/.env`:

```dotenv
GOOGLE_FACT_CHECK_API_KEY=YOUR_API_KEY_HERE
```

Keep this key private. Source Verification requires the key; text and URL classification do not.

### 5. Start the FastAPI backend

From the `backend` directory with the virtual environment active:

```bash
python -m fastapi dev main.py --port 8001
```

API documentation: **http://127.0.0.1:8001/docs**

Leave the backend terminal running while testing the website.

### 6. Configure and start the Next.js frontend

In a **separate terminal**:

```bash
cd ~/fake-news-detector/frontend  # adjust path if your project is elsewhere
npm install
```

Create `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
```

Then:

```bash
npm run dev
```

Open **http://localhost:3000**. If you change `.env.local`, restart the Next.js development server.

> The backend CORS allowlist must permit the actual frontend origin (the local implementation uses `http://localhost:3000` and `http://127.0.0.1:3000`). If Next.js uses port 3001, adjust CORS or stop the other server and run Next.js on 3000.

## How to Use

### Text Analysis

1. Open the frontend at `http://localhost:3000`.
2. Select **Text Analysis**.
3. Enter an English statement (at least 10 characters).
4. Select **Analyze News**.
5. Review the model label, confidence, and cautionary notes.

### URL Analysis

1. Select **URL Analysis**.
2. Paste a supported HTTPS article URL.
3. Select **Analyze URL**.
4. If extraction succeeds, review the headline, extracted text, prediction, and confidence.

### Source Verification

1. Run either analysis first.
2. Select **Verify with Fact-Check Sources**.
3. Review any matching claims and the original fact-checking publishers' pages.

**No matching fact checks** does not imply that a claim is true. A related claim may also differ from the claim being analyzed, so read each original report carefully.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | API status message |
| `POST` | `/api/predict` | Classify submitted text and return model confidence |
| `POST` | `/api/analyze-url` | Extract and classify a supported news article |
| `POST` | `/api/fact-check` | Search for related published fact-check reports |
| `GET` | `/docs` | Interactive Swagger documentation |

### Example: Analyze text

**Request:**

```bash
curl -X POST http://127.0.0.1:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"The United States has 50 states."}'
```

**Illustrative response shape** (values may vary by model):

```json
{
  "news": "The United States has 50 states.",
  "prediction": "REAL",
  "confidence": 75.0,
  "status": "success",
  "note": "Model probability only. Not a verified fact-check."
}
```

The `confidence` field above is a **placeholder** to show the JSON shape, not an actual computed result.

### Example: Analyze a URL

```bash
curl -X POST http://127.0.0.1:8001/api/analyze-url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.bbc.com/news/articles/REPLACE_WITH_REAL_ARTICLE_ID"}'
```

Use an actual article URL from a supported domain; the example path is not a live article.

### Example: Search fact-check sources

```bash
curl -X POST http://127.0.0.1:8001/api/fact-check \
  -H "Content-Type: application/json" \
  -d '{"query":"The Great Wall of China is visible from the Moon"}'
```

Returned items may include claim text, fact-checking publisher, rating, review title, and a link to the original report. Availability depends on Google's indexed fact-check coverage and API access.

## Troubleshooting

| Problem | Suggested check |
| --- | --- |
| `zsh: command not found: python` | Enter `backend`, activate `.venv`, or use `python3` when appropriate. |
| `Address already in use` on port 8001 | An earlier backend may still be running. Reuse it or stop its terminal before starting another. |
| Next.js says port 3000 is already in use | Use the existing dev server or stop it before restarting. |
| Frontend cannot connect to backend | Confirm the FastAPI terminal is running, the `.env.local` URL is correct, and CORS includes the frontend origin. |
| URL analysis times out | Try a normal article (not a live-update page). Publishers may block automated retrieval. |
| No matching fact checks | Google may not have a related review indexed; this is not proof of truth. |
| `AI Model not found` | Run `python train_model.py` from `backend` and confirm the model file exists. |
| Source verification fails | Confirm the API is enabled, your key is valid, and API restrictions/quota permit requests. |

## Security and Responsible Use

- Do **not** commit `backend/.env`, API keys, `.venv/`, `node_modules/`, or other secrets.
- Load `joblib` model files **only from trusted sources**, because loading untrusted serialized models is unsafe.
- The URL analyzer uses an HTTPS domain allowlist, disables redirects, and caps response sizes. Additional protections and tests are recommended before public deployment.
- Limit access, request sizes, and rate of requests in any publicly deployed version.
- Do not present classifier output as verified factual truth. Check claims against the linked sources and consider the article's date, context, and evidence.

Suggested `.gitignore` entries:

```gitignore
backend/.env
backend/.venv/
backend/__pycache__/
frontend/.env.local
frontend/node_modules/
frontend/.next/
.DS_Store
```

## Vercel Deployment
try it out via= ai-powered-fake-news-detector-bay.vercel.app
