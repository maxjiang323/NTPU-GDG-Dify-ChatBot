import { describe, it, expect } from "vitest";
import { sanitizeHtml, sanitizeUrl, sanitizeRedirectUrl } from "../sanitize";

describe("sanitizeHtml", () => {
  it("should allow safe HTML tags", () => {
    const input = "<p>Hello <strong>world</strong></p>";
    expect(sanitizeHtml(input)).toBe(input);
  });

  it("should remove script tags", () => {
    const input = '<p>Hello <script>alert("XSS")</script></p>';
    expect(sanitizeHtml(input)).toBe("<p>Hello </p>");
  });

  it("should remove event handlers like onerror and keep valid src", () => {
    const input = '<img src="https://example.com/a.png" onerror="alert(1)">';
    const output = sanitizeHtml(input);
    expect(output).not.toContain("onerror");
    // DOMPurify might change order or add/remove quotes, but let's check for the presence of src
    expect(output).toContain('src="https://example.com/a.png"');
  });

  it('should add rel="noopener noreferrer" to target="_blank" links', () => {
    const input =
      '<a href="https://example.com" target="_blank">External Link</a>';
    const output = sanitizeHtml(input);
    // Note: If this fails, it might be due to DOMPurify's default behavior or hook issue
    expect(output).toContain('rel="noopener noreferrer"');
    expect(output).toContain('target="_blank"');
  });

  it("should filter dangerous CSS classes on allowed tags", () => {
    // using span instead of div because div is not in ALLOWED_TAGS
    const input =
      '<span class="fixed top-0 left-0 bg-red-500 font-bold">Injected UI</span>';
    const output = sanitizeHtml(input);
    expect(output).not.toContain("fixed");
    expect(output).not.toContain("top-0");
    expect(output).toContain("font-bold");
  });

  it("should allow safe data:image URIs", () => {
    const safeData =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
    const input = `<img src="${safeData}">`;
    expect(sanitizeHtml(input)).toContain(safeData);
  });

  it("should remove dangerous data: URIs (e.g. SVG or HTML)", () => {
    const dangerousData =
      "data:image/svg+xml;base64,PHN2Zy9vbmxvYWQ9YWxlcnQoMSk+";
    const input = `<img src="${dangerousData}">`;
    const output = sanitizeHtml(input);
    expect(output).not.toContain(dangerousData);
    expect(output).toBe("<img>");
  });
});

describe("sanitizeUrl", () => {
  it("should allow safe http/https URLs", () => {
    // Note: braintree-sanitize-url or URL parser might add trailing slash
    const result = sanitizeUrl("https://google.com");
    expect(result.replace(/\/$/, "")).toBe("https://google.com");
  });

  it("should allow safe relative paths", () => {
    expect(sanitizeUrl("/dashboard")).toBe("/dashboard");
  });

  it("should block javascript: protocols", () => {
    expect(sanitizeUrl("javascript:alert(1)")).toBe("about:blank");
  });

  it("should handle undefined or empty input", () => {
    expect(sanitizeUrl(undefined)).toBe("about:blank");
    expect(sanitizeUrl("")).toBe("about:blank");
  });
});

describe("sanitizeRedirectUrl", () => {
  it("should allow relative paths starting with /", () => {
    expect(sanitizeRedirectUrl("/profile")).toBe("/profile");
  });

  it("should block protocol-relative URLs (//example.com)", () => {
    expect(sanitizeRedirectUrl("//google.com")).toBe("/");
  });

  it("should block cross-origin absolute URLs", () => {
    expect(sanitizeRedirectUrl("https://malicious.com/steal")).toBe("/");
  });

  it("should allow same-origin absolute URLs (stripping origin)", () => {
    const origin = window.location.origin;
    const sameOrigin = origin + "/settings";
    expect(sanitizeRedirectUrl(sameOrigin)).toBe("/settings");
  });
});

describe("CSP Alignment (Content Security Policy)", () => {
  /**
   * 這些測試確保我們的清理邏輯與 base.py 中的 CSP 設定一致。
   * CSP 策略概要：
   * - script-src: SELF, NONCE (不允許 'unsafe-inline')
   * - style-src: SELF, 'unsafe-inline'
   * - img-src: SELF, data:, https:
   */

  it("should forbid <style> tags (preventing CSS Injection, aligned with strict style-src)", () => {
    // 雖然 CSP style-src 可能允許某些 unsafe-inline，但 sanitize.ts 為了防禦 CSS Injection
    // 仍然全面禁止 <style> 標籤，這是一種深度防禦行為。
    const input = "<style>body { background: red; }</style><p>Content</p>";
    expect(sanitizeHtml(input)).toBe("<p>Content</p>");
  });

  it("should strip inline event handlers (consistent with script-src no unsafe-inline)", () => {
    // 我們的 CSP 在 script-src 中沒有排除 'unsafe-inline'，因此所有的 inline event handlers 都會被瀏覽器攔截。
    // sanitizeHtml 也應該主動移除它們。
    const input = '<img src="https://example.com/a.png" onerror="alert(1)">';
    const output = sanitizeHtml(input);
    expect(output).not.toContain("onerror");
    expect(output).toContain('src="https://example.com/a.png"');
  });

  it("should allow images from https sources (consistent with img-src allowing https:)", () => {
    const input = '<img src="https://trusted.site/image.jpg">';
    expect(sanitizeHtml(input)).toContain(
      'src="https://trusted.site/image.jpg"',
    );
  });

  it("should allow safe data:image URIs (consistent with img-src and font-src allowing data:)", () => {
    const safeData =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
    const input = `<img src="${safeData}">`;
    expect(sanitizeHtml(input)).toContain(safeData);
  });
});
