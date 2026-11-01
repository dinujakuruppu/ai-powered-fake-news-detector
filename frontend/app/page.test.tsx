
import {
  describe,
  it,
  expect,
  vi,
  afterEach,
} from "vitest";

import {
  render,
  screen,
  fireEvent,
  cleanup,
} from "@testing-library/react";

import "@testing-library/jest-dom/vitest";
import Home from "./page";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("AI Fake News Detector", () => {

  // Test 1: Check website title
  it("displays website title", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", {
        name: "AI Fake News Detector",
      })
    ).toBeInTheDocument();
  });

  // Test 2: Check text validation
  it("rejects short news text", async () => {
    render(<Home />);

    fireEvent.change(
      screen.getByLabelText("Enter News Text"),
      { target: { value: "short" } }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Analyze News",
      })
    );

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent(
      "Enter at least 10 characters."
    );
  });

  // Test 3: Check invalid URL
  it("rejects HTTP news URLs", async () => {
    render(<Home />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "URL Analysis",
      })
    );

    fireEvent.change(
      screen.getByLabelText(
        "Enter News Article URL"
      ),
      {
        target: {
          value: "http://example.com/news",
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Analyze URL",
      })
    );

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent(
      "Enter a valid HTTPS news article URL."
    );
  });

  // Test 4: Check AI prediction result
  it("displays prediction result", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        prediction: "REAL",
        confidence: 80,
        news: "This is a sample news statement.",
        status: "success",
        note: "Test prediction",
      }),
    });

    vi.stubGlobal("fetch", mockFetch);

    render(<Home />);

    fireEvent.change(
      screen.getByLabelText("Enter News Text"),
      {
        target: {
          value: "This is a sample news statement.",
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Analyze News",
      })
    );

    expect(
      await screen.findByText("REAL")
    ).toBeInTheDocument();

    expect(
      screen.getByText("80.00%")
    ).toBeInTheDocument();
  });

});
