from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions

def enforce_csrf(request):
    """
    Enforce CSRF validation for cookie-based authentication.
    """
    check = CSRFCheck(lambda x: None)  # Dummy view function
    # CSRFCheck expects a view method to check against, so we wrap it
    
    # process_view returns None if CSRF is valid, or raises an exception/returns response if not
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        # Django's CSRF middleware returns a response on failure (reason)
        # We want to raise a DRF exception
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom Authentication class that reads JWT from HttpOnly cookies.
    """
    
    def authenticate(self, request):
        # Try retrieving the token from cookies
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access_token') or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        # Optional: Enforce CSRF if using cookies for state-changing requests
        # if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        #     enforce_csrf(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
