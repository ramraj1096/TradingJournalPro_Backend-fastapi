from fastapi_mail import ConnectionConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MAIL_USERNAME=os.getenv("MAIL_USERNAME")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
MAIL_FROM=os.getenv("MAIL_FROM")
MAIL_PORT=os.getenv("MAIL_PORT")
MAIL_SERVER=os.getenv("MAIL_SERVER")
MAIL_TLS=True
MAIL_SSL=False

mail_conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_TLS=MAIL_TLS,
    MAIL_SSL=MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)