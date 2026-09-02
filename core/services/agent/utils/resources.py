from typing import Optional

from core.models import Tenant, TenantUser, User


def fetch_user(user_id: int) -> User:
  return User.objects.get(id=user_id, deleted_at__isnull=True)


def fetch_tenant_user(
  user_id: int,
  tenant_id: Optional[int] = None,
) -> TenantUser | None:
  if tenant_id is None:
    return None
  return TenantUser.available.get(user_id=user_id, tenant_id=tenant_id)


def fetch_tenant(tenant_id: Optional[int] = None) -> Tenant | None:
  if tenant_id is None:
    return None
  return Tenant.objects.get(id=tenant_id, deleted_at__isnull=True)
