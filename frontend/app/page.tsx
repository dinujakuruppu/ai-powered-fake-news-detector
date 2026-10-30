
"use client";

import { useState, type FormEvent } from "react";
import FactCheckResults from "./components/FactCheckResults";

type Mode = "text" | "url";

type Result = {
  prediction: string;
  note: string;
  news?: string;
  headline?: string;
  extracted_text?: string;
  confidence?: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8001";

export default function Home() {
  const [mode, setMode] = useState<Mode>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    const isURL = mode === "url";

    const endpoint = isURL
      ? "/api/analyze-url"
      : "/api/predict";

    const payload = isURL
      ? { url: url.trim() }
      : { text: text.trim() };

    if (!isURL && text.trim().length < 10) {
      setError("Enter at least 10 characters.");
      setLoading(false);
      return;
    }

    if (isURL) {
      try {
        if (new URL(url.trim()).protocol !== "https:") {
          throw new Error("Invalid URL");
        }
      } catch {
        setError("Enter a valid HTTPS news article URL.");
        setLoading(false);
        return;
      }
    }

    try {
      const response = await fetch(
        `${API_URL}${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
          signal: AbortSignal.timeout(30000),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Analysis failed"
        );
      }

      setResult(data);
    } catch (err) {
      if (
        err instanceof Error &&
        (err.name === "TimeoutError" ||
          err.name === "AbortError")
      ) {
        setError(
          "News website response timed out. " +
          "Try another news article or paste its text."
        );
      } else {
        setError(
          err instanceof Error
            ? err.message
            : "Cannot connect to backend."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-16 text-white">
      <div className="mx-auto max-w-2xl">

        {/* Website Header */}
        <header className="mb-10 text-center">
          <div className="mb-4 text-5xl">🧠</div>

          <h1 className="text-4xl font-bold">
            AI Fake News Detector
          </h1>

          <p className="mt-4 text-slate-400">
            AI-Powered News Classification System
          </p>
        </header>

        {/* Analysis Input Section */}
        <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          {/* Analysis Tabs */}
          <div className="mb-6 grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => {
                setMode("text");
                setResult(null);
                setError("");
              }}
              className={`rounded-xl p-3 font-semibold ${
                mode === "text"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              Text Analysis
            </button>

            <button
              type="button"
              onClick={() => {
                setMode("url");
                setResult(null);
                setError("");
              }}
              className={`rounded-xl p-3 font-semibold ${
                mode === "url"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              URL Analysis
            </button>
          </div>

          <form onSubmit={analyze}>
            {mode === "text" ? (
              <>
                <label
                  htmlFor="news-text"
                  className="mb-3 block font-semibold"
                >
                  Enter News Text
                </label>

                <textarea
                  id="news-text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste news text here..."
                  rows={6}
                  className="w-full rounded-xl border border-slate-600 bg-slate-800 p-4 outline-none focus:border-blue-500"
                />
              </>
            ) : (
              <>
                <label
                  htmlFor="news-url"
                  className="mb-3 block font-semibold"
                >
                  Enter News Article URL
                </label>

                <input
                  id="news-url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.bbc.com/news/..."
                  className="w-full rounded-xl border border-slate-600 bg-slate-800 p-4 outline-none focus:border-blue-500"
                />

                <p className="mt-3 text-sm text-slate-400">
                  Supported: BBC, Reuters, AP News,
                  The Guardian, NPR
                </p>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full rounded-xl bg-blue-600 p-3 font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading
                ? "Analyzing..."
                : mode === "text"
                  ? "Analyze News"
                  : "Analyze URL"}
            </button>

            {error && (
              <p role="alert" className="mt-4 text-red-400">
                {error}
              </p>
            )}
          </form>
        </section>

        {/* Analysis Result */}
        {result && (
          <section
            aria-live="polite"
            className="mt-6 rounded-2xl border border-slate-700 bg-slate-900 p-6"
          >
            <h2 className="mb-4 text-xl font-bold">
              Analysis Result
            </h2>

            {/* Article Headline */}
            {result.headline && (
              <p className="mb-4 font-semibold">
                {result.headline}
              </p>
            )}

            {/* Model Prediction */}
            <div
              className={`rounded-xl p-5 text-center ${
                result.prediction === "REAL"
                  ? "bg-green-950 text-green-300"
                  : "bg-red-950 text-red-300"
              }`}
            >
              <p className="text-sm">
                Model Prediction
              </p>

              <p className="mt-2 text-3xl font-bold">
                {result.prediction}
              </p>
            </div>

            {/* Model Confidence */}
            {typeof result.confidence === "number" &&
              Number.isFinite(result.confidence) && (
                <div className="mt-5 rounded-xl bg-slate-800 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="font-medium text-slate-200">
                      Model Confidence
                    </span>

                    <span className="font-bold text-blue-400">
                      {result.confidence.toFixed(2)}%
                    </span>
                  </div>

                  {/* Confidence Progress Bar */}
                  <div className="h-3 w-full overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full rounded-full bg-blue-500 transition-all duration-500"
                      style={{
                        width: `${Math.max(
                          0,
                          Math.min(100, result.confidence)
                        )}%`,
                      }}
                    />
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    Model class probability only.
                    This is not the probability
                    that the news is true.
                  </p>
                </div>
              )}

            {/* Extracted Article */}
            {result.extracted_text && (
              <div className="mt-5">
                <h3 className="mb-2 font-semibold">
                  Extracted Article
                </h3>

                <p className="max-h-48 overflow-y-auto rounded-lg bg-slate-800 p-3 text-sm text-slate-300">
                  {result.extracted_text}
                </p>
              </div>
            )}

            {/* Model Note */}
            <p className="mt-4 text-sm text-slate-400">
              {result.note}
            </p>

            {/* SOURCE VERIFICATION - NEW FEATURE */}
            <FactCheckResults
              key={`${mode}-${result.news || result.headline || ""}`}
              query={
                mode === "url"
                  ? result.headline ||
                    result.extracted_text ||
                    ""
                  : result.news || text
              }
            />

            {/* Safety Notice */}
            <p className="mt-4 text-sm text-amber-400">
              Verify important claims using reliable
              independent sources.
            </p>
          </section>
        )}

        {/* Website Footer */}
        <p className="mt-8 text-center text-sm text-slate-500">
          AI prediction only — not a verified fact-check.
        </p>
      </div>
    </main>
  );
}
