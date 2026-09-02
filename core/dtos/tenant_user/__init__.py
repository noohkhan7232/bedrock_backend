from django.conf import settings
from pydantic import BaseModel, EmailStr, Field


class CreateInvitedTenantUserDTO(BaseModel):
  email: EmailStr
  invitation_code: str = Field(min_length=1, max_length=settings.TENANT_INVITATION_CODE_LENGTH)
  role_uid: int


class CreateAdminTenantUserDTO(BaseModel):
  user_id: int
  tenant_id: int


class DeleteCurrentTenantUserDTO(BaseModel):
  actor_tenant_user_id: int


class DeleteTenantUserDTO(BaseModel):
  actor_tenant_user_id: int
  target_tenant_user_id: int


class UpdateTenantUserRoleDTO(BaseModel):
  actor_tenant_user_id: int
  target_tenant_user_id: int
  role_uid: int
