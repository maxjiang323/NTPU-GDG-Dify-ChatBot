import DOMPurify from 'dompurify';
import { sanitizeUrl as braintreeSanitizeUrl } from '@braintree/sanitize-url';

/**
 * 建立 Purifier 執行個體
 */
const purifier = DOMPurify();

/**
 * 根據 Beyond XSS 建議，加強對屬性的檢查
 */
purifier.addHook('afterSanitizeAttributes', (node) => {
    // 1. 確保所有標向新視窗的連結都具備安全性 (防護 Tabnabbing)
    if (node.tagName === 'A' && node.getAttribute('target') === '_blank') {
        node.setAttribute('rel', 'noopener noreferrer');
    }

    // 2. Class 劫持與 UI 欺騙防護 (防護惡意 Tailwind 注入)
    // 只允許特定的安全前綴，避免攻擊者利用 fixed, absolute 等類別遮蔽 UI
    if (node.hasAttribute('class')) {
        const classNames = node.getAttribute('class')?.split(/\s+/) || [];
        const filteredClasses = classNames.filter(cls =>
            cls.startsWith('prose-') ||
            cls.startsWith('markdown-') ||
            // 允許特定的排版類別（安全名單）
            /^text-(left|center|right|justify)$/.test(cls) ||
            /^font-(bold|semibold|normal|light|italic)$/.test(cls)
        );

        if (filteredClasses.length > 0) {
            node.setAttribute('class', filteredClasses.join(' '));
        } else {
            node.removeAttribute('class');
        }
    }

    // 3. 數據協議安全性檢查 (再度強化)
    // 雖然有 ALLOWED_URI_REGEXP，但有些環境下 DOMPurify 對 data: URI 的處理可能較寬鬆
    // 我們在此強制檢查並移除任何非安全格式的 data: URI (特別是 svg+xml)
    const uriAttrs = ['src', 'href'];
    uriAttrs.forEach(attr => {
        if (node.hasAttribute(attr)) {
            const val = node.getAttribute(attr);
            if (val && /^data:/i.test(val)) {
                const isSafeData = /^data:image\/(?:png|jpeg|jpg|gif|webp);base64,/i.test(val);
                if (!isSafeData) {
                    node.removeAttribute(attr);
                }
            }
        }
    });
});

/**
 * 工業級資安清理機制 (修正版)
 */
export const sanitizeHtml = (html: string): string => {
    return purifier.sanitize(html, {
        ALLOWED_TAGS: [
            'p', 'br', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li',
            'code', 'pre', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'span', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
        ],
        ALLOWED_ATTR: [
            'href', 'title', 'target', 'rel', 'src', 'alt', 'class'
        ],

        // 嚴格限制協議，徹底杜絕 javascript: 偽協議及其編碼繞過
        ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel)|data:image\/(?:png|jpeg|jpg|gif|webp);base64)/i,

        // 強制禁用危險行為
        FORBID_TAGS: ['style'], // 預防 CSS 注入
        FORBID_ATTR: ['id', 'name'], // 預防 DOM Clobbering
    });
};

/**
 * 進階 URL 安全清理 (防護 Redirect XSS 與 javascript: 偽協議)
 * 參考：https://github.com/braintree/sanitize-url
 * 參考：https://aszx87410.github.io/beyond-xss/ch1/javascript-protocol/
 */
export const sanitizeUrl = (url: string | undefined): string => {
    if (!url) return 'about:blank';

    // 1. 使用工業級 sanitize-url 庫進行初步清理
    let sanitized = braintreeSanitizeUrl(url);

    // 2. 結合 JavaScript URL 解析進行二次校驗 (Beyond XSS 建議)
    if (sanitized !== 'about:blank') {
        try {
            // 如果是相對路徑 (以 / 開頭，且不以 // 開頭)，在 SPA 中通常是安全的
            if (sanitized.startsWith('/') && !sanitized.startsWith('//')) {
                return sanitized;
            }

            const parsed = new URL(sanitized, window.location.origin);
            // 嚴格限制協議：僅允許 http: 與 https:
            if (!['http:', 'https:'].includes(parsed.protocol)) {
                return 'about:blank';
            }
        } catch (e) {
            // 解析失敗或格式異常，則退回約定的預設值
            return 'about:blank';
        }
    }

    return sanitized;
};

/**
 * 針對重新導向的 URL 安全清理 (防止 Open Redirect)
 * 僅允許：
 * 1. 相對路徑 (e.g., /login, /dashboard)
 * 2. 與當前網站同源的絕對路徑
 */
export const sanitizeRedirectUrl = (url: string | undefined): string => {
    if (!url) return '/';

    try {
        // 1. 處理相對路徑
        if (url.startsWith('/') && !url.startsWith('//')) {
            return url;
        }

        // 2. 處理絕對路徑 (必須同源)
        const parsed = new URL(url, window.location.origin);
        if (parsed.origin === window.location.origin) {
            return parsed.pathname + parsed.search + parsed.hash;
        }
    } catch (e) {
        // 解析失敗
    }

    // 預設回首頁
    return '/';
};

/**
 * 針對 CSS 內容的特定清理 (針對 ChartStyle 等使用 dangerouslySetInnerHTML 的情況)
 * 目的：防止透過 </style> 標籤逃逸並執行 XSS，以及防護基本 CSS 注入
 */
export const sanitizeCss = (css: string): string => {
    // 1. 基本 HTML 清理（防止 <style> 跳脫）
    let clean = purifier.sanitize(css, {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: [],
        RETURN_DOM: false,
        RETURN_DOM_FRAGMENT: false,
    });

    // 2. 移除 </style> 字串，物理性防止標籤逃逸
    clean = clean.replace(/<\/style>/gi, "");

    // 3. 過濾 CSS url(...) 設定 (防止 javascript: 偽協議或惡意外部連線)
    clean = clean.replace(/url\s*\(([^)]+)\)/gi, (match, url) => {
        // 移除引號與多餘空白
        const trimmedUrl = url.trim().replace(/^(['"])(.*)\1$/, '$2');
        return `url("${sanitizeUrl(trimmedUrl)}")`;
    });

    // 4. 移除 expression(...) (針對舊版 IE 的 CSS 執行漏洞防護)
    clean = clean.replace(/expression\s*\([^)]*\)/gi, "");

    return clean;
};
