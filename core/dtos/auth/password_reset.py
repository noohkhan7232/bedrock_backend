from django.conf import settings
from pydantic import BaseModel, EmailStr, Field


class SendPasswordResetCodeDTO(BaseModel):
  email: EmailStr


class ResetPasswordDTO(BaseModel):
  email: EmailStr
  reset_code: str = Field(min_length=1, max_length=settings.PASSWORD_RESET_CODE_LENGTH)
  password: str = Field(min_length=8, max_length=255)


class GetEmailFromCodeDTO(BaseModel):
  reset_code: str = Field(min_length=1, max_length=settings.PASSWORD_RESET_CODE_LENGTH)
