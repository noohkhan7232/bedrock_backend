from typing import Any

from django.conf import settings
from pydantic import BaseModel, EmailStr, Field


class CreateUserDTO(BaseModel):
  email: EmailStr
  first_name: str = Field(min_length=1, max_length=255)
  last_name: str = Field(min_length=1, max_length=255)
  password: str = Field(default='', max_length=255)

  headline: str = Field(default='', max_length=255)
  location: str = Field(default='', max_length=255)

  sso_code: str = Field(default='', max_length=255)
  invitation_code: str = Field(default='', max_length=settings.TENANT_INVITATION_CODE_LENGTH)
  verification_code: str = Field(default='', max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH)


class UpdateUserImageDTO(BaseModel):
  user_id: int
  image: Any


class UpdateUserPasswordDTO(BaseModel):
  user_id: int
  password: str = Field(min_length=1, max_length=255)
  new_password: str = Field(min_length=1, max_length=255)


class DeleteCurrentUserDTO(BaseModel):
  actor_user_id: int
