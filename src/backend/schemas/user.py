from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class ChatRequest(BaseModel):
    question: str
    user_id: str | None = "guest"

