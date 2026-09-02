from django.db import models

from core.models.base import BaseModel
from core.models.choices import TenantLimitKey


class TenantLimitOverride(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  LimitKey = TenantLimitKey

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  limit_key = models.CharField(
    max_length=64,
    choices=TenantLimitKey.choices,
  )
  value = models.IntegerField()

  class Meta(BaseModel.Meta):
    db_table = 'tenant_limit_overrides'
    constraints = [
      models.UniqueConstraint(
        fields=['tenant', 'limit_key'],
        name='unique_tenant_limit_override',
      ),
    ]

  def __str__(self) -> str:
    return (
      f'(id:{self.id})tenant_id={self.tenant_id}, '
      f'{self.limit_key}={self.value}'
    )
