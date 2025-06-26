from django.db import models

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core_apps.common.models import TimeStampedModel

User  = get_user_model()


class BankAccount(TimeStampedModel):
    class AccountType(models.TextChoices):
        CURRENT = ("current",_("Current"))
        SAVINGS = ("savings", _("Savings"))

    class AccountStatus(models.TextChoices):
        ACTIVE = ("active", _("Active"))
        INACTIVE = ("in-active",_("In-active"))

    class AccountCurrency(models.TextChoices):
        DOLLAR = ("us_dollar", _("Dollar"))
        POUND_STERLING = ("pound_sterling", _("Pound Sterling"))
        RUPEES = ("indian_rupees", _("Indian Rupees"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_accounts")
    account_number = models.CharField(_("Account Number"), max_length=20, unique=True)
    account_balance = models.DecimalField(_("Account Balance"), decimal_places=3, max_digits=10, default=0.00)
    currency = models.CharField(_("Currency"), max_length=20, choices=AccountCurrency.choices, default=AccountCurrency.DOLLAR)
    account_status = models.CharField(_("Account Status"), max_length=10, choices=AccountStatus.choices, default=AccountStatus.INACTIVE)
    account_type = models.CharField(_("Account Type"), max_length=20, choices=AccountType.choices, default=AccountType.SAVINGS)
    is_primary = models.BooleanField(_("Primary Account"), default=False)
    kyc_submitted = models.BooleanField(_("KYC Submitted"), default=False)
    kyc_verified = models.BooleanField(_("KYC Submitted"), default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="verified_accounts")
    verification_date = models.DateTimeField(_("Verification Date"), null=True, blank=True)
    verification_notes = models.TextField(_("Verification Notes"), blank=True)
    fully_activated = models.BooleanField(_("Fully Activated"), default=False)

    def __str__(self):
        return f"{self.user.full_name}'s {self.get_currency_display()} - {self.get_account_type_display()} Account - {self.account_number}"

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        unique_together = ["user", "currency", "account_type"]

    def clean(self):
        if self.account_balance < 0:
            raise ValidationError(_("Account balance cannot be negative"))
        
    def save(self, *args, **kwargs):
        if self.is_primary:
            BankAccount.objects.filter(user=self.user).update(is_primary=False)
        super().save(*args, **kwargs)


class Transaction(TimeStampedModel):
    class TransactionStatus(models.TextChoices):
        PENDING = ("pending", _("Pending"))
        COMPLETED = ("completed", _("Completed"))
        FAILED = ("failed", _("Failed"))

    class TransactionType(models.TextChoices):
        DEPOSIT = ("deposit", _("Deposit"))
        WITHDRAWAL = ("withdrawal", _("Withdrawal"))
        TRANSFER = ("transfer", _("Transfer"))

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="transactions")
    amount = models.DecimalField(_("Amount"), decimal_places=2, max_digits=10, default=0.00)
    description = models.CharField(_("Description"), max_length=500, null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="received_transactions")
    sender =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_transactions")
    receiver_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name="received_transactions",
    )
    sender_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_transactions",
    )
    status = models.CharField(choices=TransactionStatus.choices, max_length=20, default=TransactionStatus.PENDING)
    transaction_type = models.CharField(choices=TransactionType.choices, max_length=20)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.status}"
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]
        