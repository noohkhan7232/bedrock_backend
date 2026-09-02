from django.db import models
from django.db.models import Q

from core.constants import TENANT_USER_ROLES
from core.models.managers import AvailableManager
from core.models.base import BaseModel
from core.models.mixins import SoftDeleteMixin


class TenantUser(SoftDeleteMixin, BaseModel):
  _soft_delete_parent_paths = ('tenant', 'user',)
  _field_requirements = {'active': True}

  available = AvailableManager()

  tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
  user = models.ForeignKey('User', on_delete=models.CASCADE)
  title = models.CharField(max_length=255, blank=True, default='')
  description = models.TextField(blank=True, default='')
  disable_email_notification = models.BooleanField(default=False)
  role_uid = models.IntegerField(default=TENANT_USER_ROLES.MEMBER.uid)
  active = models.BooleanField(default=True)
  joined_at = models.DateTimeField(auto_now_add=True)

  class Meta(BaseModel.Meta):
    db_table = 'tenant_users'
    constraints = [
      models.UniqueConstraint(
        fields=['tenant_id', 'user_id'],
        name='unique_tenant_user',
        condition=Q(deleted_at__isnull=True),
      ),
    ]

  @classmethod
  def get_id_from(cls, tenant_id, user_id):
    return cls.objects.get(tenant_id=tenant_id, user_id=user_id).id

  @property
  def is_admin(self) -> bool:
    return self.role_uid == TENANT_USER_ROLES.ADMIN.uid

  @property
  def is_manager(self) -> bool:
    return self.role_uid == TENANT_USER_ROLES.MANAGER.uid

  @property
  def is_member(self) -> bool:
    return self.role_uid == TENANT_USER_ROLES.MEMBER.uid

  def __str__(self) -> str:
    return (
      f'({self.id})tenant_id={self.tenant_id}, user_id={self.user_id}, '
      f'role_uid={self.role_uid}, active={self.active}'
    )
