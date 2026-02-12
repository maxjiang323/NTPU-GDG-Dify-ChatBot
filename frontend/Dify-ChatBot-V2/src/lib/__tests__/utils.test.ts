import { describe, it, expect } from "vitest";
import { cn } from "../utils";

describe("cn utility", () => {
  it("should merge class names correctly", () => {
    expect(cn("c1", "c2")).toBe("c1 c2");
  });

  it("should handle conditional classes", () => {
    const isTrue = true;
    const isFalse = false;
    expect(cn("c1", isTrue && "c2", isFalse && "c3")).toBe("c1 c2");
  });

  it("should merge tailwind classes using tailwind-merge (override logic)", () => {
    // tailwind-merge should override p-2 with p-4 if they conflict
    expect(cn("p-2", "p-4")).toBe("p-4");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("should handle mixed inputs (arrays, objects)", () => {
    expect(cn("c1", ["c2", "c3"], { c4: true, c5: false })).toBe("c1 c2 c3 c4");
  });
});
