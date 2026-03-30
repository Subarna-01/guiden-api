from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.modules.email.schemas import Email
from app.modules.email.service import EmailService

email_router = APIRouter(prefix="/email", tags=["email"])

email_service = EmailService()


@email_router.post("/send")
async def send(request_body: Email) -> JSONResponse:
    return await email_service.send(request_body)
