import { fetchWithTimeout } from '@/lib/fetchWithTimeout';
import { sanitizeRedirectUrl } from '@/lib/sanitize';

interface RequestOptions extends RequestInit {
    headers?: Record<string, string>;
}

let internalCsrfToken: string | undefined = undefined;

export const getCsrfToken = () => {
    return internalCsrfToken;
};

const performLogout = async (redirectPath: string = "/login") => {
    const csrfToken = getCsrfToken();
    try {
        // Use fetchWithTimeout directly to avoid the global request interceptor logic for 401
        await fetchWithTimeout(`/api/auth/logout/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            },
            credentials: "include"
        }, 30000);
    } catch (error) {
        console.error("Logout API failed", error);
    } finally {
        internalCsrfToken = undefined;
        localStorage.clear();

        // 安全跳轉：防止 javascript: 偽協議 XSS
        // 安全跳轉：防止 Open Redirect 與 javascript: 偽協議
        // 使用 sanitizeRedirectUrl 強制檢查同源策略
        const safePath = sanitizeRedirectUrl(redirectPath);
        window.location.href = safePath;
    }
};

const request = async (endpoint: string, options: RequestOptions = {}, isRetry = false): Promise<any> => {
    const csrfToken = getCsrfToken();

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    // Add CSRF token for methods that require it
    if (csrfToken && ["POST", "PUT", "PATCH", "DELETE"].includes(options.method || "GET")) {
        headers["X-CSRFToken"] = csrfToken;
    }

    const response = await fetchWithTimeout(`/api${endpoint}`, {
        ...options,
        headers,
        credentials: "include", // Ensure cookies are sent with requests
    }, 30000);


    if (response.status === 401) {
        // Token expired or invalid
        if (endpoint.includes("/auth/status/")) {
            if (!isRetry) {
                console.log("Auth check failed, retrying once...");
                await new Promise(resolve => setTimeout(resolve, 500));
                return request(endpoint, options, true);
            }
            // 如果 retry 也失敗，不做 return，讓下面 !response.ok 的邏輯去拋出錯誤
        } else if (!endpoint.includes("/auth/logout/")) {
            console.log("Unauthorized request, clearing state and redirecting to landing...");
            performLogout("/");
            return;
        }
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "API Request Failed");
    }

    if (response.status === 204) {
        return null;
    }

    const data = await response.json().catch(() => null);

    // Automatically update CSRF token if returned in response body
    if (data && data.csrfToken) {
        internalCsrfToken = data.csrfToken;
    }

    return data;
};

export const api = {
    // Check authentication status with backend
    checkAuth: () => request("/auth/status/", { method: "GET" }),

    // Logout: Clear cookies by calling backend (if applicable) or relying on browser
    // Since we use HttpOnly cookies, we can't clear them from JS. 
    // We should call a logout endpoint. existing allauth logout might redirect.
    // For now, we assume the frontend just redirects to login, 
    // but proper logout should hit an API. 
    // We will just redirect to /accounts/logout/ for now or expect the user to handle it.
    // For this refactor, we remove local token management.
    logout: performLogout,

    getSessions: () => request("/chat/sessions/"),
    getMessages: (sessionId: string) => {
        if (sessionId.startsWith('temp-')) return Promise.resolve([]);
        return request(`/chat/messages/?session=${sessionId}`);
    },

    createSession: (topic: string) =>
        request("/chat/sessions/", {
            method: "POST",
            body: JSON.stringify({ topic }),
        }),

    createMessage: (sessionId: string, content: string, role: 'USER' | 'AI' | 'SYSTEM') => {
        if (sessionId.startsWith('temp-')) return Promise.resolve(null);
        return request("/chat/messages/", {
            method: "POST",
            body: JSON.stringify({ session: sessionId, content, role }),
        });
    },

    updateSession: (sessionId: string, topic: string) => {
        if (sessionId.startsWith('temp-')) return Promise.resolve(null);
        return request(`/chat/sessions/${sessionId}/`, {
            method: "PATCH",
            body: JSON.stringify({ topic }),
        });
    },

    deleteSession: (sessionId: string) => {
        if (sessionId.startsWith('temp-')) return Promise.resolve(null);
        return request(`/chat/sessions/${sessionId}/`, {
            method: "DELETE",
        });
    },
};