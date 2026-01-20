from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import PermissionDenied

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        email = sociallogin.user.email
        if not email:
            raise PermissionDenied("Email is required for login.")

        allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])
        
        # If no domains are restricted, allow all
        if not allowed_domains:
            return

        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            from django.contrib import messages
            from allauth.exceptions import ImmediateHttpResponse
            from django.shortcuts import redirect
            import urllib.parse
            
            # 直接中斷 Allauth 流程，重定向回登入頁，並帶上錯誤代碼
            raise ImmediateHttpResponse(redirect("/login?err_code=DOMAIN_RESTRICTED"))
