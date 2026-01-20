import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * 保護路由組件
 * - 當 isChecking === true 時，顯示 loading (不做任何重定向)
 * - 當 isChecking === false && isAuthenticated === true 時，顯示內容
 * - 當 isChecking === false && isAuthenticated === false 時，重定向到 /login
 */
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isChecking, isAuthenticated, error } = useAuth();


  // 關鍵：只有在確認了 auth 狀態（isChecking === false）後，才做決定
  if (isChecking) {
    // 正在確認 auth 狀態，顯示 loading
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">驗證登入狀態中...</p>
          {error && <p className="text-sm text-destructive mt-2">狀態: {error}</p>}
        </div>
      </div>
    );
  }

  // isChecking === false，auth 狀態已確認
  if (!isAuthenticated) {
    // 未驗證，重定向到 /login
    return <Navigate to="/login" replace />;
  }

  // 已驗證，顯示受保護的內容
  return <>{children}</>;
}
