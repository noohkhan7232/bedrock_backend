from typing import Any

from django.conf import settings
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EnqueueEmailJobDTO(BaseModel):
  model_config = ConfigDict(extra='forbid')

  tenant_id: int | None = Field(default=None, ge=1)
  sender_user_id: int | None = Field(default=None, ge=1)

  email_type: str = Field(min_length=1, max_length=64)
  to_email: EmailStr
  template_vars: dict[str, Any] = Field(default_factory=dict)
  dedupe_key: str | None = Field(default=None, min_length=1, max_length=255)


class SignupWelcomeTemplateVarsDTO(BaseModel):
  model_config = ConfigDict(extra='allow')
  schema_version: int = 1


class EmailVerificationTemplateVarsDTO(BaseModel):
  model_config = ConfigDict(extra='allow')
  schema_version: int = 1
  verification_code: str = Field(min_length=1, max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH)


class PasswordResetTemplateVarsDTO(BaseModel):
  model_config = ConfigDict(extra='allow')
  schema_version: int = 1
  reset_code: str = Field(min_length=1, max_length=settings.PASSWORD_RESET_CODE_LENGTH)


class TenantInviteTemplateVarsDTO(BaseModel):
  model_config = ConfigDict(extra='allow')
  schema_version: int = 1
  invitation_code: str = Field(min_length=1, max_length=settings.TENANT_INVITATION_CODE_LENGTH)
