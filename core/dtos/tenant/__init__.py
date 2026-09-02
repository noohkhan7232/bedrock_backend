from datetime import datetime

from pydantic import BaseModel, Field


class CreateTenantDTO(BaseModel):
  name: str = Field(min_length=1, max_length=255)
  description: str = Field(min_length=0, max_length=1024, default='')

  user_id: int
  plan_uid: int
  months: int | None


class DeleteTenantDTO(BaseModel):
  tenant_id: int
  user_id: int


class CreateTenantDeletionRecordDTO(BaseModel):
  tenant_id: int
  tenant_name: str = Field(min_length=1, max_length=255)
  tenant_domain: str = Field(min_length=1, max_length=255)
  tenant_account_id: str = Field(min_length=1, max_length=255)
  tenant_description: str = Field(min_length=0, max_length=1024, default='')
  deletion_date: datetime


class GetTenantInvitationCodesDTO(BaseModel):
  tenant_id: int
  search: str | None = None
