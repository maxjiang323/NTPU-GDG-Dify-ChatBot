import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export default function GoogleCallback() {
    const navigate = useNavigate();
    const { checkAuthStatus } = useAuth();
    const { toast } = useToast();
    const processedRef = useRef(false);

    useEffect(() => {
        if (processedRef.current) return;
        processedRef.current = true;

        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const error = params.get('error');

        // Use the environment variable for API base URL
        const API_URL = `/api/auth/google/`;

        if (error) {
            console.error("Google Auth Error:", error);
            toast({
                variant: 'destructive',
                title: '登入失敗',
                description: 'Google 授權失敗',
            });
            navigate('/login');
            return;
        }

        if (code) {
            fetch(API_URL, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    redirect_uri: window.location.origin + '/auth/google/callback'
                }),
            })
                .then(async (res) => {
                    if (res.ok) {
                        await checkAuthStatus();
                        toast({
                            title: "登入成功",
                            description: "正在進入...",
                        });
                        navigate('/chat');
                    } else {
                        let errorMessage = 'Login failed';
                        try {
                            const data = await res.json();
                            errorMessage = data.error || errorMessage;
                        } catch (e) {
                            console.error("Failed to parse error response:", e);
                            errorMessage = `Login failed (${res.status}): ${res.statusText}`;
                        }
                        throw new Error(errorMessage);
                    }
                })
                .catch((err) => {
                    console.error(err);
                    toast({
                        variant: 'destructive',
                        title: '登入錯誤',
                        description: err.message || '無法完成登入',
                    });
                    navigate('/login');
                });
        } else {
            navigate('/login');
        }
    }, [navigate, checkAuthStatus, toast]);

    return (
        <div className="flex items-center justify-center h-screen">
            <p className="text-lg">Signing in...</p>
        </div>
    );
}
