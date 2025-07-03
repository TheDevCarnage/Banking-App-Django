from django.urls import path

from .views import (
    AccountVerificationView,
    DepositView,
    InitiateWithdrawlView,
    VerifyUsernameAndWithdrawAPIView,
)

urlpatterns = [
    path(
        "verify/<uuid:pk>/",
        AccountVerificationView.as_view(),
        name="account_verification",
    ),
    path(
        "deposit/",
        DepositView.as_view(),
        name="account_deposit",
    ),
    path(
        "initiate-withdrawl/",
        InitiateWithdrawlView.as_view(),
        name="initiate_withdrawl",
    ),
    path(
        "verify-username-and-withdraw/",
        VerifyUsernameAndWithdrawAPIView.as_view(),
        name="verify_username_and_withdraw",
    ),
]
