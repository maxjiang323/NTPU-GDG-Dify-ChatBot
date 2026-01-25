import { fetchWithTimeout } from "@/lib/fetchWithTimeout";
import { sanitizeRedirectUrl } from "@/lib/sanitize";

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

interface ApiMessage {
  id: number;
  session: string; // session ID (UUID)
  role: "USER" | "ASSISTANT" | "SYSTEM";
  content: string;
  created_at: string; // ISO 8601 字串
}

interface ApiSession {
  id: string; // UUID
  user: string; // user ID
  topic: string | null;
  dify_conversation_id: string;
  created_at: string; // ISO 8601 字串
  updated_at: string; // ISO 8601 字串
  messages: ApiMessage[];
}

let internalCsrfToken: string | undefined = undefined;

// ---------- Refresh control ----------
let isRefreshing = false;
let refreshPromise: Promise<unknown> | null = null;

// 儲存失敗時的原始請求資訊
type PendingRequest = {
  endpoint: string;
  options: RequestOptions;
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
};
let pendingRequests: PendingRequest[] = [];

// ---------- CSRF ----------
export const getCsrfToken = () => {
  return internalCsrfToken;
};

// ---------- logout ----------
const performLogout = async (redirectPath: string = "/login") => {
  const csrfToken = getCsrfToken();
  try {
    // Use fetchWithTimeout directly to avoid the global request interceptor logic for 401
    await fetchWithTimeout(
      `/api/auth/logout/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        },
        credentials: "include",
      },
      30000,
    );
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

// refresh token 並重試失敗請求
async function refreshTokenAndRetryFailedRequests() {
  try {
    const resp = await fetchWithTimeout(
      "/api/auth/refresh/",
      {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      },
      30000,
    );
    if (!resp.ok) throw new Error("refresh_token_invalid");
    const data = await resp.json();
    if (data && data.csrfToken) internalCsrfToken = data.csrfToken;
    // retry pending requests 時 clone options，避免多次使用同一個 body
    pendingRequests.forEach(({ endpoint, options, resolve, reject }) => {
      request(endpoint, { ...options }, true)
        .then(resolve)
        .catch(reject);
    });
    pendingRequests = [];
    return data;
  } catch (err) {
    // refresh 失敗，全部 pending request 視為失敗，觸發登出
    pendingRequests.forEach(({ reject }) => reject(err));
    pendingRequests = [];
    performLogout("/login");
    throw err;
  } finally {
    isRefreshing = false;
    refreshPromise = null;
  }
}

const request = async <T = unknown>(
  endpoint: string,
  options: RequestOptions = {},
  isRetry = false,
): Promise<T> => {
  const csrfToken = getCsrfToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add CSRF token for methods that require it
  if (
    csrfToken &&
    ["POST", "PUT", "PATCH", "DELETE"].includes(options.method || "GET")
  ) {
    headers["X-CSRFToken"] = csrfToken;
  }

  const response = await fetchWithTimeout(
    `/api${endpoint}`,
    {
      ...options,
      headers,
      credentials: "include", // Ensure cookies are sent with requests
    },
    30000,
  );

  if (
    response.status === 401 &&
    !isRetry &&
    !endpoint.includes("/auth/refresh/")
  ) {
    const error = await response.json().catch(() => null);

    if (error?.code === "access_token_expired") {
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = refreshTokenAndRetryFailedRequests();
      }

      return new Promise((resolve, reject) => {
        pendingRequests.push({ endpoint, options, resolve, reject });
      });
    }

    // 其他 401 直接丟錯
    throw new Error(error?.detail || "Unauthorized");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "API Error");
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);
  if (data?.csrfToken) internalCsrfToken = data.csrfToken;

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

  getSessions: (): Promise<ApiSession[]> =>
    request<ApiSession[]>("/chat/sessions/"),
  getMessages: (sessionId: string): Promise<ApiMessage[]> => {
    if (sessionId.startsWith("temp-")) return Promise.resolve([]);
    return request<ApiMessage[]>(`/chat/messages/?session=${sessionId}`);
  },

  createSession: (topic: string): Promise<ApiSession> =>
    request("/chat/sessions/", {
      method: "POST",
      body: JSON.stringify({ topic }),
    }),

  createMessage: (
    sessionId: string,
    content: string,
    role: "USER" | "AI" | "SYSTEM",
  ): Promise<ApiMessage> => {
    if (sessionId.startsWith("temp-")) return Promise.resolve(null);
    return request("/chat/messages/", {
      method: "POST",
      body: JSON.stringify({ session: sessionId, content, role }),
    });
  },

  updateSession: (sessionId: string, topic: string): Promise<ApiSession> => {
    if (sessionId.startsWith("temp-")) return Promise.resolve(null);
    return request(`/chat/sessions/${sessionId}/`, {
      method: "PATCH",
      body: JSON.stringify({ topic }),
    });
  },

  deleteSession: (sessionId: string): Promise<void> => {
    if (sessionId.startsWith("temp-")) return Promise.resolve(null);
    return request(`/chat/sessions/${sessionId}/`, {
      method: "DELETE",
    });
  },
};
