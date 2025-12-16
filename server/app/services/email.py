import logging
from abc import ABC, abstractmethod
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.models.database.access_request import AccessRequest

logger = logging.getLogger(__name__)


def get_email_service() -> EmailService:
    match settings.EMAIL_BACKEND:
        case "smtp":
            return SmtpEmailService()
        case "console":
            return ConsoleEmailService()
        case "disabled":
            return DisabledEmailService()
        case _:
            raise RuntimeError(f"Unknown EMAIL_BACKEND: {settings.EMAIL_BACKEND}")


class EmailService(ABC):
    @abstractmethod
    async def send(
        self,
        to: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None: ...

    async def send_access_request_notification(
        self, admin_email: str, access_request: AccessRequest
    ) -> None:
        """
        Notify an admin that a new access request has been submitted.
        """
        subject = f"New access request: {access_request.email}"
        body = (
            f"User {access_request.first_name} {access_request.last_name} "
            f"has requested access (request id {access_request.id})."
        )
        try:
            await self.send(to=admin_email, subject=subject, text=body)
        except Exception as e:
            logger.error(
                f"Failed to send access request notification to {admin_email}: {e}"
            )

    async def send_access_request_approved_email(
        self, access_request: AccessRequest
    ) -> None:
        """
        Notify a user that their access request was approved and provide instructions.
        """
        subject = "Access Request Approved"
        body = (
            f"Hello {access_request.first_name},\n\n"
            f"Your access request has been approved!\n"
            f"Please register to access the application."
        )
        try:
            await self.send(to=access_request.email, subject=subject, text=body)
        except Exception as e:
            logger.error(
                f"Failed to send access request approved email to {access_request.email}: {e}"
            )


class SmtpEmailService(EmailService):
    async def send(
        self,
        to: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to
        message["Subject"] = subject

        if html:
            message.set_content(text)
            message.add_alternative(html, subtype="html")
        else:
            message.set_content(text)

        kwargs = dict(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=settings.SMTP_USE_TLS,
            use_tls=settings.SMTP_USE_SSL,
            timeout=10,
        )

        # guard against including empty username/password
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            kwargs["username"] = settings.SMTP_USERNAME
            kwargs["password"] = settings.SMTP_PASSWORD

        await aiosmtplib.send(message, **kwargs)  # type: ignore


class ConsoleEmailService(EmailService):
    async def send(
        self,
        to: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        logger.info(
            "EMAIL (console)\nTo: %s\nSubject: %s\n\n%s",
            to,
            subject,
            text,
        )


class DisabledEmailService(EmailService):
    async def send(
        self,
        to: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        logger.debug("Email disabled; skipping send to %s", to)
