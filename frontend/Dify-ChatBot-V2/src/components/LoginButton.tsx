import { Button } from "@/components/ui/button";

const LoginButton = () => {
    const handleLogin = () => {
        // Redirect to Allauth Google Login
        window.location.href = `/accounts/google/login/`;
    };

    return (
        <Button onClick={handleLogin} variant="outline" className="gap-2">
            <img
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt="Google Logo"
                className="w-4 h-4"
            />
            登入 Google
        </Button>
    );
};

export default LoginButton;
