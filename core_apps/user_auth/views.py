from typing import Optional, Any
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from djoser.views import TokenCreateView, User
from loguru import logger
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .emails import send_otp
from .utils import generate_otp
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


User = get_user_model()


def set_auth_cookies(
    response: Response, access_token: str, refresh_token: Optional[str] = None
) -> None:
    access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
    cookie_settings = {
        "path": settings.COOKIE_PATH,
        "secure": settings.COOKIE_SECURE,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
        "max_age": access_token_lifetime,
    }

    response.set_cookie("access", access_token, **cookie_settings)
    if refresh_token:
        refresh_token_lifetime = settings.SIMPLE_JWT[
            "REFRESH_TOKEN_LIFETIME"
        ].total_seconds()
        refresh_cookie_settings = cookie_settings.copy()
        refresh_cookie_settings["max_age"] = refresh_token_lifetime
        response.set_cookie("refresh", refresh_token, **refresh_cookie_settings)

    logged_in_cookie_settings = cookie_settings.copy()
    logged_in_cookie_settings["httponly"] = False
    response.set_cookie("logged_in", "true", **logged_in_cookie_settings)


class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        user = serializer.user
        if user.is_locked_out:
            return Response(
                {
                    "error": f"Account is locked due to multiple failed login attempts. Please try again after {settings.LOCKOUT_DURATION.total_seconds()/60} minutes.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.reset_failed_login_attempts()

        otp = generate_otp()
        user.set_otp(otp)
        send_otp(user.email, otp)
        logger.info(f"OTP sent for login to user: {user.email}")

        return Response(
            {"success": "OTP sent to your email", "email": user.email},
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            email = request.data.get("email")
            user = User.objects.filter(email=email).first()
            if user:
                user.handle_failed_login_attempts()
                failed_attempts = user.failed_login_attempts
                logger.error(
                    f"Failed login attempts: {failed_attempts} for user: {email}"
                )

                if failed_attempts >= settings.LOGIN_ATTEMPTS:
                    return Response(
                        {
                            "error": f"You have exceeded the maximum number of login attempts. Your account has been locked for {settings.LOCKOUT_DURATION.total_seconds/60} minutes. An email has been sent to you with further instructions."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                logger.error(f"Failed login attempt with non-existent user: {email}")
                return Response(
                    {"error": "Invalid login credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return self._action(serializer)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        refresh_token = request.COOKIES.get("refresh")
        if refresh_token:
            request.data["refresh"] = refresh_token
            refresh_res = super().post(request, *args, **kwargs)

        if refresh_res.status_code == status.HTTP_200_OK:
            access_token = refresh_res.data.get("access")
            refresh_token = refresh_res.data.get("refresh")

            if access_token and refresh_token:
                set_auth_cookies(refresh_res, access_token, refresh_token)

                refresh_res.data.pop("access", None)
                refresh_res.data.pop("refresh", None)
                refresh_res.data["message"] = "Access token refreshed successfully."
            else:
                refresh_res.data[
                    "message"
                ] = "Access or refresh token not found in refresh response data"
                logger.error(
                    "Access or refresh token not found in refresh response data"
                )
        return refresh_res


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"error": "OTP is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(otp=otp, otp_expiry_time__gt=timezone.now()).first()

        if not user:
            return Response(
                {"error": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_locked_out:
            return Response(
                {
                    "error": f"Account is locked due to multiple failed login attempts. Please try again after {settings.LOCKOUT_DURATION.total_seconds()/60} minutes."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.verify_otp(otp)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = Response(
            {
                "success": "Login successful. Now add your profile information, so that we can create an account for you"
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, access_token, refresh_token)

        logger.info(f"successful login with OTP: {user.email}")
        return response


class LogoutAPIView(APIView):
    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.delete_cookie("logged_in")
        return response


class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token, uid):
        if not uid or not token:
            logger.warning("Email verification failed: Missing UID or token")
            return Response(
                {"detail": "Missing UID or token."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            logger.error(f"Email verification failed: Invalid UID {uid}")
            return Response(
                {"detail": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            logger.info(f"Email verified successfully for user: {user.email}")
            return Response(
                {"detail": "Email verified successfully."}, status=status.HTTP_200_OK
            )
        else:
            logger.warning(
                f"Email verification failed: Invalid token for user {user.email}"
            )
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
