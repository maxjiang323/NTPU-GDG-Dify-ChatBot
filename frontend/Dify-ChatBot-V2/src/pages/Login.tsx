import React, { useEffect } from "react";
import LoginButton from "@/components/LoginButton";
import { Link, useSearchParams } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const ERROR_MESSAGES: Record<string, string> = {
    "DOMAIN_RESTRICTED": "您的 Email 網域不在允許登入的名單內，請使用專屬信箱。",
    "AUTH_FAILED": "登入驗證失敗或已取消，請稍後再試。",
};

export default function Login() {
    const [searchParams] = useSearchParams();
    const { toast } = useToast();
    const errCode = searchParams.get('err_code');

    useEffect(() => {
        if (errCode && ERROR_MESSAGES[errCode]) {
            toast({
                variant: "destructive",
                title: "登入失敗",
                description: ERROR_MESSAGES[errCode],
            });
        }
    }, [errCode, toast]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 space-y-8 border">
                <div className="text-center space-y-4">
                    <Link to="/">
                        <img
                            src="/lovable-uploads/44239bf4-86bb-4b1e-ac1c-d73a9d1fb446.png"
                            alt="NTPU LawHelper Logo"
                            className="h-20 w-auto mx-auto hover:opacity-80 transition-opacity"
                        />
                    </Link>
                    <div className="space-y-2">
                        <h1 className="text-2xl font-bold tracking-tight">登入帳號</h1>
                        <p className="text-muted-foreground text-sm">
                            請登入以存取您的對話紀錄與 AI 法律助理
                        </p>
                    </div>
                </div>

                <div className="flex flex-col gap-4">
                    <LoginButton />
                </div>

                <div className="text-center">
                    <p className="text-xs text-muted-foreground">
                        登入即代表您同意本服務之服務條款與隱私權政策
                    </p>
                </div>
            </div>
        </div>
    );
}
