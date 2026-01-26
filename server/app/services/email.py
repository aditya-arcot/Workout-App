import logging
import ssl
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.models.database.access_request import AccessRequest
from app.utilities.date import get_utc_timestamp_str

logger = logging.getLogger(__name__)


def get_email_service() -> EmailService:
    match settings.email.backend:
        case "smtp" | "local":
            return SmtpEmailService()
        case "console":
            return ConsoleEmailService()
        case "disabled":
            return DisabledEmailService()


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
        subject = f"New Access Request - {settings.project_name}"
        body = (
            f"User {access_request.first_name} {access_request.last_name} ({access_request.email}) "
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
        subject = f"Access Request Approved - {settings.project_name}"
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
    use_tls = settings.email.backend == "smtp"
    tls_context = ssl.create_default_context()
    tls_context.check_hostname = False
    tls_context.verify_mode = ssl.CERT_NONE

    async def send(
        self,
        to: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        now = get_utc_timestamp_str(datetime.now(timezone.utc))
        logger.info("Sending email to %s with subject %s (%s)", to, subject, now)

        message = EmailMessage()
        message["From"] = settings.email.email_from
        message["To"] = to
        message["Subject"] = subject

        if html:
            message.set_content(text)
            message.add_alternative(html, subtype="html")
        else:
            message.set_content(text)

        kwargs = dict(
            hostname=settings.email.smtp_host,
            port=settings.email.smtp_port,
            start_tls=self.use_tls,
            timeout=10,
            tls_context=self.tls_context if self.use_tls else None,
        )

        if settings.email.smtp_username and settings.email.smtp_password:
            kwargs["username"] = settings.email.smtp_username
            kwargs["password"] = settings.email.smtp_password

        resp = await aiosmtplib.send(message, **kwargs)  # type: ignore
        logger.info("Email sent to %s with subject %s (%s)", to, subject, now)
        logger.debug("SMTP response: %s", resp)


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
