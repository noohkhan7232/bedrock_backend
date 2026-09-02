from django.db import models

from core.constants import PLANS
from core.models.base import BaseModel


class Subscription(BaseModel):
  _soft_delete_parent_paths = ('tenant',)

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  plan_uid = models.IntegerField(default=PLANS.FREE.uid)
  subscribed_at = models.DateField(null=True)
  expires_at = models.DateField(null=True)

  class Meta(BaseModel.Meta):
    db_table = 'subscriptions'

  def __str__(self) -> str:
    return f'({self.id})tenant_id={self.tenant_id}, {self.plan_uid}'
