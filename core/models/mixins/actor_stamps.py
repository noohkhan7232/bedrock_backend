from typing import TypedDict

from django.db import models

from core.models.tenant_user import TenantUser
from core.models.user import User


class DefaultSnapshotItem(TypedDict):
  user_id: int
  tenant_user_id: int | None
  display_name: str


def get_default_snapshot(
  user_id: int,
  tenant_user_id: int | None,
  first_name: str,
  last_name: str,
) -> DefaultSnapshotItem:
  return {
    'user_id': user_id,
    'tenant_user_id': tenant_user_id,
    'display_name': f'{first_name} {last_name}',
  }


def get_tenant_user_snapshot(
  tenant_user: TenantUser
) -> DefaultSnapshotItem:
  return get_default_snapshot(
    user_id=tenant_user.user.id,
    tenant_user_id=tenant_user.id,
    first_name=tenant_user.user.first_name,
    last_name=tenant_user.user.last_name,
  )


def get_user_snapshot(user: User) -> DefaultSnapshotItem:
  return get_default_snapshot(
    user_id=user.id,
    tenant_user_id=None,
    first_name=user.first_name,
    last_name=user.last_name,
  )


class ActorStampedMixin(models.Model):
  created_by_snapshot = models.JSONField(blank=True, default=dict)
  updated_by_snapshot = models.JSONField(blank=True, default=dict)

  class Meta:
    abstract = True


class TenantUserStampMixin(ActorStampedMixin):
  created_by_tenant_user = models.ForeignKey(
    'TenantUser',
    null=True,
    on_delete=models.SET_NULL,
    related_name='+',
  )
  updated_by_tenant_user = models.ForeignKey(
    'TenantUser',
    null=True,
    on_delete=models.SET_NULL,
    related_name='+',
  )

  class Meta:
    abstract = True

  def stamp_created_by(self, tenant_user: TenantUser) -> None:
    self.created_by_tenant_user = tenant_user
    self.updated_by_tenant_user = tenant_user
    snapshot = get_tenant_user_snapshot(tenant_user=tenant_user)
    self.created_by_snapshot = snapshot
    self.updated_by_snapshot = snapshot

  def stamp_updated_by(self, tenant_user: TenantUser) -> None:
    self.updated_by_tenant_user = tenant_user
    snapshot = get_tenant_user_snapshot(tenant_user=tenant_user)
    self.updated_by_snapshot = snapshot


class UserStampedMixin(ActorStampedMixin):
  created_by_user = models.ForeignKey(
    'User',
    null=True,
    on_delete=models.SET_NULL,
    related_name='+',
  )
  updated_by_user = models.ForeignKey(
    'User',
    null=True,
    on_delete=models.SET_NULL,
    related_name='+',
  )

  class Meta:
    abstract = True

  def stamp_created_by(self, user: User) -> None:
    self.created_by_user = user
    self.updated_by_user = user
    snapshot = get_user_snapshot(user=user)
    self.created_by_snapshot = snapshot
    self.updated_by_snapshot = snapshot

  def stamp_updated_by(self, user: User) -> None:
    self.updated_by_user = user
    snapshot = get_user_snapshot(user=user)
    self.updated_by_snapshot = snapshot
