import random
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException,status
from fastapi_mail import FastMail, MessageSchema
from app.models.email import EmailSchema
from app.config.mail_config import mail_conf
from app.config.templates import REGISTER_OTP_TEMPLATE, LOGIN_OTP_TEMPLATE, RESET_OTP_TEMPLATE

router = APIRouter()

# In-memory OTP cache
otp_cache = {}

def generate_otp() -> str:
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def save_otp(email: str, otp: str):
    """Saves OTP with a timestamp."""
    otp_cache[email] = {"otp": otp, "timestamp": time.time()}

@router.post("/send-otp/" , tags=["email"], status_code=status.HTTP_200_OK )
async def send_email(email: EmailSchema, background_tasks: BackgroundTasks, name: str):
    try:
        otp = generate_otp()
        save_otp(email.email, otp)  

        if email.use_case == "register":
            html_body = REGISTER_OTP_TEMPLATE.format(otp=otp, name=name)
        elif email.use_case == "login":
            html_body = LOGIN_OTP_TEMPLATE.format(otp=otp, name=name)
        elif email.use_case == "reset":
            html_body = RESET_OTP_TEMPLATE.format(otp=otp, name=name)
        else:
            raise HTTPException(status_code=400, detail="Invalid use case")

        message = MessageSchema(
            subject=email.subject,
            recipients=[email.email],
            body=html_body,
            subtype="html"
        )

        fm = FastMail(mail_conf)
        background_tasks.add_task(fm.send_message, message)
        return {"message": "Email has been sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.post("/verify-otp/", tags=["email"], status_code=status.HTTP_200_OK)
async def verify_otp(email: str, otp: str):
    """Verifies the provided OTP."""
    if email not in otp_cache:
        raise HTTPException(status_code=404, detail="OTP not found")

    saved_otp = otp_cache[email]["otp"]
    timestamp = otp_cache[email]["timestamp"]

    if saved_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if time.time() - timestamp > 300:
        del otp_cache[email]
        raise HTTPException(status_code=400, detail="OTP expired")

    del otp_cache[email]
    return {"message": "OTP verified successfully"}
