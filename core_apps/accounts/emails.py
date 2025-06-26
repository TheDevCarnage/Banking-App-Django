from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger

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