from django.db import models

from core.models.base import BaseModel


class TenantUserLink(BaseModel):
  _soft_delete_parent_paths = ('tenant_user',)

  tenant_user = models.ForeignKey(
    'TenantUser',
    on_delete=models.CASCADE,
  )
  name = models.CharField(max_length=1024)
  url = models.CharField(max_length=1024)
  display_order = models.IntegerField(blank=True, default=0)

  class Meta(BaseModel.Meta):
    db_table = 'tenant_user_links'

  def __str__(self) -> str:
    return (
      f'({self.id})tenant_user_id={self.tenant_user_id}, {self.url}'
    )
