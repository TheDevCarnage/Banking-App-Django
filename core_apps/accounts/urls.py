from django.urls import path

from .views import AccountVerificationView, DepositView

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
]
