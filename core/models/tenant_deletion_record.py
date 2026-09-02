from django.db import models

from core.models.base import BaseModel
from core.models.mixins.actor_stamps import TenantUserStampMixin


class TenantDeletionRecord(TenantUserStampMixin, BaseModel):
  tenant_id = models.IntegerField()
  tenant_name = models.CharField(max_length=255)
  tenant_domain = models.CharField(max_length=255)
  tenant_account_id = models.CharField(max_length=255)
  tenant_description = models.CharField(
    max_length=1024,
    blank=True,
    default='',
  )
  deletion_date = models.DateTimeField()

  class Meta(BaseModel.Meta):
    db_table = 'tenant_deletion_records'

  def __str__(self) -> str:
    return (
      f'({self.id})tenant_id={self.tenant_id}, '
      f'deletion_date={self.deletion_date}'
    )
