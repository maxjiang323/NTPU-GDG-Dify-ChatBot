from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from config.settings.base import COOKIE_SECURE, COOKIE_SAMESITE
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return JsonResponse({'detail': 'no_refresh_token'}, status=401)

        try:
            refresh = RefreshToken(refresh_token)

            # SimpleJWT 會自動處理 rotation / blacklist
            new_access = str(refresh.access_token)
            new_refresh = str(refresh)  # 若有 rotate，這裡會是新的

            response = JsonResponse({
                'access': new_access,
                'csrfToken': get_token(request),
            })

            response.set_cookie(
                'access_token',
                new_access,
                httponly=True,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=60 * 60,  # 與 SIMPLE_JWT ACCESS_TOKEN_LIFETIME 對齊
            )

            response.set_cookie(
                'refresh_token',
                new_refresh,
                httponly=True,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=60 * 60 * 24,  # 與 SIMPLE_JWT REFRESH_TOKEN_LIFETIME 對齊
            )

            return response

        except TokenError:
            response = JsonResponse({'detail': 'refresh_token_invalid'}, status=401)
            response.delete_cookie('access_token', samesite=COOKIE_SAMESITE)
            response.delete_cookie('refresh_token', samesite=COOKIE_SAMESITE)
            return response
