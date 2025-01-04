from pydantic import BaseModel, EmailStr

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    body: str
    use_case : str
