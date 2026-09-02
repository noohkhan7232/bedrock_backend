from django.db import models

from core.models.base import BaseModel


class TenantTag(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  name = models.CharField(max_length=255)

  class Meta(BaseModel.Meta):
    db_table = 'tenant_tags'
    constraints = [
      models.UniqueConstraint(
        fields=['tenant_id', 'name'],
        name='unique_tenant_tag',
      ),
    ]

  def __str__(self) -> str:
    return f'({self.id}){self.name}, tenant_id={self.tenant_id}'
