from django.db import models

from core.models.base import BaseModel


class TenantWhitelistedEmail(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  email = models.EmailField(max_length=255)

  class Meta(BaseModel.Meta):
    db_table = 'tenant_whitelisted_emails'
    constraints = [
      models.UniqueConstraint(
        fields=['tenant', 'email'],
        name='unique_tenant_whitelisted_email',
      ),
    ]

  def __str__(self) -> str:
    return f'({self.id}){self.email}, tenant_id={self.tenant_id}'
