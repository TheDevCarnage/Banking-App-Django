from django.urls import path

from .views import (
    CustomTokenCreateView,
    CustomTokenRefreshView,
    LogoutAPIView,
    OTPVerifyView,
    EmailVerificationView,
)

urlpatterns = [
    path("login/", CustomTokenCreateView.as_view(), name="login"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify_otp"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="refresh"),
    path(
        "activate/<str:uid>/<str:token>/",
        EmailVerificationView.as_view(),
        name="activate",
    ),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
