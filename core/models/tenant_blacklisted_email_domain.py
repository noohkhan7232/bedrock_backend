from django.db import models

from core.models.base import BaseModel


class TenantBlacklistedEmailDomain(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  domain = models.CharField(max_length=255)
  include_subdomains = models.BooleanField(default=False)

  class Meta(BaseModel.Meta):
    db_table = 'tenant_blacklisted_email_domains'
    constraints = [
      models.UniqueConstraint(
        fields=['tenant', 'domain'],
        name='unqiue_tenant_blacklisted_email_domain',
      ),
    ]

  def __str__(self) -> str:
    return f'({self.id}){self.domain}, tenant_id={self.tenant_id}'
