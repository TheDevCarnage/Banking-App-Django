from typing import Any

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from core_apps.common.permissions import IsAccountExecutive, IsTeller
from core_apps.common.renderers import GenericJSONRenderer
from .emails import send_full_activation_email, send_deposit_confirmation_email
from .models import BankAccount
from .serializers import (
    AccountVerificationSerializer,
    CustomerInfoSerializer,
    DepositSerializer,
)
from django.db import transaction
from loguru import logger


class AccountVerificationView(generics.UpdateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = AccountVerificationSerializer
    permission_classes = [IsAccountExecutive]
    renderer_classes = [GenericJSONRenderer]
    object_label = "verification"

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        if instance.kyc_verified and instance.fully_activated:
            return Response(
                {
                    "message": "This account has already been verified and fully activated."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        partial = kwargs.get("partial", False)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid(raise_exception=True):
            kyc_submitted = serializer.validated_data.get(
                "kyc_submitted", instance.kyc_submitted
            )
            kyc_verified = serializer.validated_data.get(
                "kyc_verified", instance.kyc_verified
            )

            if kyc_verified and not kyc_submitted:
                return Response(
                    {"error": "KYC must be submitted before it can be verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            instance.kyc_submitted = kyc_submitted
            instance.save()

            if kyc_submitted and kyc_verified:
                instance.kyc_verified = kyc_verified
                instance.verification_date = serializer.validated_data.get(
                    "kyc_verification_date", timezone.now()
                )
                instance.verification_notes = serializer.validated_data.get(
                    "verification_notes", ""
                )
                instance.verified_by = request.user
                instance.fully_activated = True
                instance.account_status = BankAccount.AccountStatus.ACTIVE
                instance.save()

                send_full_activation_email(instance)

                return Response(
                    {
                        "message": "Account verification status activated successfully.",
                        "data": self.get_serializer(instance).data,
                    }
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositView(generics.CreateAPIView):
    serializer_class = DepositSerializer
    renderer_classes = [GenericJSONRenderer]
    object_label = "deposit"
    permission_classes = [IsTeller]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        account_number = request.query_params.get("account_number")
        if not account_number:
            return Response(
                {"error": "Account Number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            account = BankAccount.objects.get(account_number=account_number)
            serializer = CustomerInfoSerializer(account)
            return Response(serializer.data)
        except BankAccount.DoesNotExist:
            return Response(
                {"error": "Account Number does not exists."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        account = serializer.context["account"]
        amount = serializer.validated_data["amount"]
        try:
            account.account_balance += amount
            account.full_clean()
            account.save()
            logger.info(
                f"Deposit of amount {amount} was made to account number {account.account_number} by teller {request.user.email}"
            )

            send_deposit_confirmation_email(
                user=account.user,
                user_email=account.user.email,
                amount=amount,
                currency=account.currency,
                account_number=account.account_number,
                new_balance=account.account_balance,
            )
            return Response(
                {
                    "message": f"Successfully deposited {amount} to account {account.account_number}",
                    "new_balance": str(account.account_balance),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error during deposit: {str(e)}")
            return Response(
                {"error": "An error occured during deposit."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
