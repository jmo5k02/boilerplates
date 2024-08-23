from fastapi import APIRouter
from pydantic.networks import EmailStr

from src._common.emails.test import generate_test_email, send_email

router = APIRouter()

@router.post("/test-email", status_code=201)
async def test_email(email_to: EmailStr):
    email_data = generate_test_email(email_to)
    send_email(
        email_to=email_to,
        subject=email_data["subject"],
        html_content=email_data["html_content"],
    )
    return {"message": "Test email sent"}