import smtplib
import datetime
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.settings import settings
from app.modules.email.enum import EmailTemplate
from app.modules.email.schemas import Email


class EmailService:
    def __init__(self) -> None:
        pass

    def render_template(self, template_name: str, context: dict) -> str:
        template = settings.TEMPLATE_ENV.get_template(f"email/{template_name}")
        return template.render(**context)

    async def send(self, request_body: Email) -> JSONResponse:
        try:
            _email_subject = ""
            _html_body = ""

            if request_body.template_name == EmailTemplate.VERIFY_OTP.value:
                _email_subject = "Verify Your OTP"

                _html_body = self.render_template(
                    "verify_otp.html",
                    {
                        "otp": request_body.otp,
                        "current_year": datetime.datetime.now().year,
                    },
                )

            elif request_body.template_name == EmailTemplate.SIGNUP_CONFIRMATION.value:
                _email_subject = "Sign Up Confirmation"

                _html_body = self.render_template(
                    "signup_confirmation.html",
                    {
                        "email": request_body.to,
                        "current_year": datetime.datetime.now().year,
                    },
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email template provided",
                )

            message = MIMEMultipart()
            message["From"] = settings.SMTP_USER
            message["To"] = request_body.to
            message["Subject"] = _email_subject
            message.attach(MIMEText(_html_body, "html"))

            try:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(message)

            except Exception as e:
                raise e

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Request queued"},
            )

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )
