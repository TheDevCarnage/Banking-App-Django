from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger
from core_apps.accounts.models import BankAccount


def send_account_creation_email(user, bank_account):
    subject = _("Your New Bank Account has been Created.")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    context = {
        "user": user,
        "site_name": settings.SITE_NAME,
        "account": bank_account,
    }

    html_email = render_to_string("emails/account_created.html", context=context)
    plain_email = strip_tags(html_email)

    email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
    email.attach_alternative(html_email, "text/html")

    try:
        email.send()
        logger.info(f"Account Created email sent to: {user.email}")
    except Exception as e:
        logger.error("Failed to send account created email to: {email}: Error {str(e)}")


def send_full_activation_email(account: BankAccount) -> None:
    subject = _("Your Bank Account is now fully activayed.")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [account.user.email]

    context = {
        "site_name": settings.SITE_NAME,
        "account": account,
    }

    html_email = render_to_string("emails/bank_account_activated.html", context=context)
    plain_email = strip_tags(html_email)

    email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
    email.attach_alternative(html_email, "text/html")

    try:
        email.send()
        logger.info(f"Account fully activated email sent to: {account.user.email}")
    except Exception as e:
        logger.error(
            "Failed to send Fully Activated email to: {account.user.email}: Error {str(e)}"
        )


def send_deposit_confirmation_email(
    user, user_email, amount, currency, account_number, new_balance
) -> None:
    subject = _("Deposit Confirmation")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    context = {
        "site_name": settings.SITE_NAME,
        "user": user,
        "amount": amount,
        "currency": currency,
        "new_balance": new_balance,
        "account_number": account_number,
    }

    html_email = render_to_string("emails/deposit_confirmation.html", context=context)
    plain_email = strip_tags(html_email)

    email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
    email.attach_alternative(html_email, "text/html")

    try:
        email.send()
        logger.info(f"Deposit Confirmation email sent to: {user_email}")
    except Exception as e:
        logger.error(
            "Failed to send Deposit Confirmation email to: {user_email}: Error {str(e)}"
        )
