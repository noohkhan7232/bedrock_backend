from django.db import models

from core.constants import TENANT_EMAIL_DEFAULT_POLICIES
from core.models.base import BaseModel


class TenantEmailPolicyConfig(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE)
  default_policy_uid = models.IntegerField(
    default=TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid,
  )
  email_whitelist_overrides_blacklist = models.BooleanField(
    default=False,
  )

  class Meta(BaseModel.Meta):
    db_table = 'tenant_email_policy_configs'

  def __str__(self) -> str:
    return (
      f'({self.id}){self.default_policy_uid}, '
      f'tenant_id={self.tenant_id}'
    )
