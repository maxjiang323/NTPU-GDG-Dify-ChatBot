import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";

function HelloWorld({ name }: { name: string }) {
  return <h1>Hello {name}</h1>;
}

describe("HelloWorld Component", () => {
  it("renders the correct name", () => {
    render(<HelloWorld name="Vitest" />);
    // "Hello Vitest" should be in the document
    expect(screen.getByText("Hello Vitest")).toBeInTheDocument();
  });

  it("basic math works", () => {
    expect(1 + 1).toBe(2);
  });
});
