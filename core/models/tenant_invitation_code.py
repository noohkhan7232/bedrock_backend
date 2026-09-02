import datetime

from django.conf import settings
from django.db import models

from core.models.base import BaseModel
from core.utils.clock import get_utc_now
from core.utils.text import generate_random_letters


class TenantInvitationCode(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  email = models.EmailField(max_length=255)
  invitation_code = models.CharField(
    max_length=settings.TENANT_INVITATION_CODE_LENGTH,
    unique=True,
  )
  invited_at = models.DateTimeField(auto_now_add=True)
  valid_until = models.DateTimeField()
  invited_by = models.ForeignKey(
    'TenantUser',
    null=True,
    on_delete=models.SET_NULL,
  )

  class Meta(BaseModel.Meta):
    db_table = 'tenant_invitation_codes'

  def issue_invitation(self, tenant_user_id: int):
    self.invited_by_id = tenant_user_id

    code_length = settings.TENANT_INVITATION_CODE_LENGTH
    lifetime_hours = settings.TENANT_INVITATION_CODE_LIFETIME_HOURS

    self.invitation_code = generate_random_letters(length=code_length)
    self.invited_at = get_utc_now()
    self.valid_until = get_utc_now() + datetime.timedelta(hours=lifetime_hours)

  def set_invitation_code(self):
    self.invitation_code = generate_random_letters(
      length=settings.TENANT_INVITATION_CODE_LENGTH,
    )
    self.valid_until = get_utc_now() + datetime.timedelta(
      hours=settings.TENANT_INVITATION_CODE_LIFETIME_HOURS,
    )

  def update_invitation_date(self):
    self.invited_at = get_utc_now()
    self.valid_until = get_utc_now() + datetime.timedelta(
      hours=settings.TENANT_INVITATION_CODE_LIFETIME_HOURS,
    )

  def __str__(self) -> str:
    return f'({self.id})invitation code for {self.email}'
