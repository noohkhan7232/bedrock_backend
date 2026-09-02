from django.conf import settings
from pydantic import BaseModel, EmailStr, Field


class AcceptTenantInvitationDTO(BaseModel):
  user_id: int
  invitation_code: str = Field(min_length=1, max_length=settings.TENANT_INVITATION_CODE_LENGTH)


class DeclineTenantInvitationDTO(BaseModel):
  user_id: int
  invitation_code: str = Field(min_length=1, max_length=settings.TENANT_INVITATION_CODE_LENGTH)


class InviteToTenantDTO(BaseModel):
  tenant_id: int
  tenant_user_id: int
  emails: list[EmailStr]


class GetEmailFromCodeDTO(BaseModel):
  invitation_code: str


class GetTenantFromCodeDTO(BaseModel):
  invitation_code: str
