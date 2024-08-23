import logging
import emails
from pathlib import Path
from jinja2 import Template

from settings import global_settings as settings

def generate_test_email(email_to: str):
    subject = "Test email"
    html_content = render_email_template(
        template_name="test-email.html",
        context={"email_to": email_to, "project_name": settings.PROJECT_NAME},
    )
    return {"subject": subject, "html_content": html_content}

def render_email_template(*, template_name: str, context: dict[str, any]) -> str:
    template_str = (
        Path(__file__).parent.parent.parent / "emails" / "templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content

def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logging.info(f"send email result: {response}")