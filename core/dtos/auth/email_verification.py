from django.conf import settings

from pydantic import BaseModel, EmailStr, Field


class GetEmailAvailabilityDTO(BaseModel):
  email: EmailStr


class GetEmailFromCodeDTO(BaseModel):
  verification_code: str = Field(min_length=1, max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH)


class IssueEmailVerificationCodeDTO(BaseModel):
  email: EmailStr
