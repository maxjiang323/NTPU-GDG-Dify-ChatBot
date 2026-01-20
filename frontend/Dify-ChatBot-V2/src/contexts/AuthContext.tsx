import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api } from "@/services/api";

interface AuthContextType {
  // 三態 auth system
  isChecking: boolean;  // 正在確認 auth 狀態
  isAuthenticated: boolean;  // 已驗證
  error: string | null;  // 錯誤訊息
  checkAuthStatus: () => Promise<void>;  // 主動觸發檢查
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isChecking, setIsChecking] = useState(true);  // 初始化時設為 true，表示正在檢查
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    setIsChecking(true);
    setError(null);
    try {
      const response = await api.checkAuth();
      setIsAuthenticated(true);
      setError(null);
    } catch (err) {
      // Auth status check failed (expected if not logged in)
      setIsAuthenticated(false);
      setError(err instanceof Error ? err.message : "Authentication check failed");
    } finally {
      setIsChecking(false);
    }
  };

  // App mount 時檢查一次 auth status
  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <AuthContext.Provider value={{ isChecking, isAuthenticated, error, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
