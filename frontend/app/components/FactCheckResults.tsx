
"use client";

import { useState } from "react";

type FactCheckItem = {
  claim: string;
  publisher: string;
  rating: string;
  title: string;
  url: string;
  review_date: string;
};

type FactCheckResponse = {
  status: string;
  results: FactCheckItem[];
  note: string;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8001";

export default function FactCheckResults({
  query,
}: {
  query: string;
}) {
  const [data, setData] =
    useState<FactCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function verifySources() {
    setLoading(true);
    setError("");
    setData(null);

    try {
      const response = await fetch(
        `${API_URL}/api/fact-check`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: query.trim().slice(0, 500),
          }),
          signal: AbortSignal.timeout(20000),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Source verification failed."
        );
      }

      setData(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch fact checks."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-6 rounded-xl border border-slate-700 bg-slate-800 p-5">
      <h3 className="text-lg font-bold">
        Source Verification
      </h3>

      <p className="mt-2 text-sm text-slate-400">
        Search for related published fact checks.
      </p>

      <button
        type="button"
        onClick={verifySources}
        disabled={loading || query.trim().length < 10}
        className="mt-4 w-full rounded-xl bg-indigo-600 p-3 font-semibold hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading
          ? "Searching Sources..."
          : "Verify with Fact-Check Sources"}
      </button>

      {error && (
        <p role="alert" className="mt-4 text-red-400">
          {error}
        </p>
      )}

      {data && (
        <div className="mt-5 space-y-4">
          {data.results.length === 0 ? (
            <p className="rounded-lg bg-slate-900 p-4 text-amber-300">
              No matching published fact checks found.
              This does not mean the claim is true.
            </p>
          ) : (
            data.results.map((item, index) => (
              <div
                key={`${item.url}-${index}`}
                className="rounded-xl bg-slate-900 p-4"
              >
                <p className="font-semibold text-white">
                  {item.publisher}
                </p>

                <p className="mt-2 text-sm text-slate-300">
                  Claim: {item.claim}
                </p>

                <p className="mt-2 text-sm text-amber-300">
                  Publisher Rating: {item.rating}
                </p>

                {item.title && (
                  <p className="mt-2 text-sm text-slate-300">
                    {item.title}
                  </p>
                )}

                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-block text-sm font-medium text-blue-400 hover:underline"
                >
                  Read Original Fact Check
                </a>
              </div>
            ))
          )}

          <p className="text-xs text-slate-400">
            {data.note}
          </p>
        </div>
      )}
    </div>
  );
}
