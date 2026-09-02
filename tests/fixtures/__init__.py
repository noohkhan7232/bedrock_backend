import time
from types import SimpleNamespace

import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from factory import Iterator

from tests.constants import PLANS
from tests.factories.tenant_factory import TenantFactory
from tests.factories.tenant_user_factory import TenantUserFactory
from tests.factories.user_factory import UserFactory


pytest_plugins =['tests.fixtures']

SEED_SIZES = {
  'free': SimpleNamespace(
    TENANTS_COUNT=2,
    TENANT_USERS_COUNT_BY_ROLE={
      'admin': 1,
      'manager': 1,
      'member': 30,
    },
    ADMINS_COUNT=1,
    MANAGERS_COUNT=1,
    TENANT_USERS_COUNT=30,
  ),
  'standard': SimpleNamespace(
    TENANTS_COUNT=2,
    TENANT_USERS_COUNT_BY_ROLE={
      'admin': 1,
      'manager': 1,
      'member': 30,
    },
    ADMINS_COUNT=1,
    MANAGERS_COUNT=1,
    TENANT_USERS_COUNT=30,
  ),
  'enterprise': SimpleNamespace(
    TENANTS_COUNT=2,
    TENANT_USERS_COUNT_BY_ROLE={
      'admin': 1,
      'manager': 1,
      'member': 30,
    },
    ADMINS_COUNT=1,
    MANAGERS_COUNT=1,
    TENANT_USERS_COUNT=30,
  ),
}

@pytest.fixture(scope='session', autouse=True)
def use_fast_hasher():
  settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

@pytest.fixture(scope='session', autouse=True)
def clear_all_records(django_db_setup, django_db_blocker):
  with django_db_blocker.unblock():
    call_command('flush', verbosity=0, interactive=False)

@pytest.fixture(scope='session', autouse=True)
def default_seed(django_db_setup, django_db_blocker):
  t0 = time.perf_counter()
  tenants_by_plan = { plan: [] for plan in PLANS }
  tenant_users_by_tenant = {} # { tenant_id: { role: [TenantUser, ...] } }

  with django_db_blocker.unblock():
    users_count = 0
    for plan in PLANS:
      seed_sizes = SEED_SIZES[plan]
      for _ in range(seed_sizes.TENANTS_COUNT):
        for _, count in seed_sizes.TENANT_USERS_COUNT_BY_ROLE.items():
          users_count += count

    users = UserFactory.create_batch(users_count)

    start_index = 0
    for plan in PLANS:
      seed_sizes = SEED_SIZES[plan]
      tenants = TenantFactory.create_batch(
        seed_sizes.TENANTS_COUNT, plan=plan)
      tenants_by_plan[plan] = tenants

      for tenant in tenants:
        tenant_users_by_tenant[tenant.id] = {}

        for role, count in seed_sizes.TENANT_USERS_COUNT_BY_ROLE.items():
          tenant_users = TenantUserFactory.create_batch(
            size=count,
            role=role,
            tenant=tenant,
            user=Iterator(
              users[start_index:start_index+count],
              cycle=False,
            ),
          )
          start_index += count
          tenant_users_by_tenant[tenant.id][role] = tenant_users

  dt = time.perf_counter() - t0
  print(f'[default_seed] setup took {dt:.2f}sec')
  return SimpleNamespace(
    tenants=tenants_by_plan,
    tenant_users=tenant_users_by_tenant,
  )

@pytest.fixture(scope='session', autouse=True)
def seed_reference_tables(django_db_setup, django_db_blocker):
  with django_db_blocker.unblock():
    with transaction.atomic():
      # If reference tables are needed, initialize here.
      pass
