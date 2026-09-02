import random

from core.constants import TENANT_USER_ROLES
from core.models import Tenant, TenantUser, User
from core.services.test_data.tenant_user_seed import (
  TITLES,
  DESCRIPTIONS,
)
from core.utils.clock import get_utc_now


def build_tenant_user_instance(
  rng: random.Random,
  tenant_id: int,
  user_id: int,
  role_uid: int,
) -> TenantUser:
  title = ''
  if rng.random() < 0.8:
    title = rng.choice(TITLES)

  description = ''
  if rng.random() < 0.8:
    length = rng.choice(list(DESCRIPTIONS.keys()))
    description = rng.choice(DESCRIPTIONS[length])

  return TenantUser(
    tenant_id=tenant_id,
    user_id=user_id,
    title=title,
    description=description,
    role_uid=role_uid,
    disable_email_notification=rng.random() < 0.5,
    active=True,
    joined_at=get_utc_now(),
  )


def create_test_tenant_users(
  rng: random.Random,
  tenant_domain: str,
  count: int,
  admins_count: int,
  managers_count: int,
  batch_size: int = 500,
) -> list[TenantUser]:
  try:
    tenant = Tenant.objects.get(domain=tenant_domain)
  except Tenant.DoesNotExist:
    raise ValueError('Tenant not found.')

  existing_tenant_users = (
    TenantUser.objects.filter(tenant__domain=tenant_domain)
  )
  if User.objects.all().count() < count + len(existing_tenant_users):
    raise ValueError(f'Create {count} users first.')
  if count < admins_count:
    raise ValueError('Too many admins.')
  if count < managers_count:
    raise ValueError('Too many managers.')
  if count < admins_count + managers_count:
    raise ValueError('Too many admins and managers.')

  tenant_id = tenant.id

  existing_tenant_user_user_ids = [
    tenant_user.user.id for tenant_user in existing_tenant_users
  ]
  user_id_candidates = [
    user.id for user in User.objects.all()
    if user.id not in existing_tenant_user_user_ids
  ]
  user_ids = rng.sample(population=user_id_candidates, k=count)

  existing_admins = TenantUser.objects.filter(
    tenant__domain=tenant_domain,
    role_uid=TENANT_USER_ROLES.ADMIN.uid,
  )
  existing_admin_user_ids = [admin.user.id for admin in existing_admins]
  admin_user_id_candidates = [
    user_id for user_id in user_ids if user_id not in existing_admin_user_ids
  ]
  admin_user_ids = rng.sample(
    population=admin_user_id_candidates,
    k=admins_count,
  )

  existing_managers = TenantUser.objects.filter(
    tenant__domain=tenant_domain,
    role_uid=TENANT_USER_ROLES.MANAGER.uid,
  )
  existing_manager_user_ids = [manager.user.id for manager in existing_managers]
  manager_user_id_candidates = [
    user_id for user_id in user_ids
    if user_id not in existing_manager_user_ids and user_id not in admin_user_ids
  ]
  manager_user_ids = rng.sample(
    population=manager_user_id_candidates,
    k=managers_count,
  )

  tenant_users: list[TenantUser] = []
  for user_id in user_ids:
    role_uid = TENANT_USER_ROLES.MEMBER.uid
    if user_id in admin_user_ids:
      role_uid = TENANT_USER_ROLES.ADMIN.uid
    elif user_id in manager_user_ids:
      role_uid = TENANT_USER_ROLES.MANAGER.uid

    tenant_user = build_tenant_user_instance(
      rng=rng,
      tenant_id=tenant_id,
      user_id=user_id,
      role_uid=role_uid,
    )
    tenant_users.append(tenant_user)

  tenant_users = TenantUser.objects.bulk_create(
    tenant_users,
    batch_size=batch_size,
  )

  return tenant_users
