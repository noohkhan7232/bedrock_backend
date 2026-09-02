import random

from django.db import transaction

from core.constants import PLANS
from core.dtos.tenant import CreateTenantDTO
from core.models import Tenant, User
from core.services.subscription import subscribe
from core.services.tenant import create_tenant
from core.services.test_data.tenant_seed import (
  TENANT_DESCRIPTION_LENGTHS,
  TENANT_DESCRIPTION_TEMPLATES,
)


def get_tenant_name() -> str:
  count = Tenant.all_objects.count()
  return f'Workspace {count+1:03d}'


def create_test_tenant(
  rng: random.Random,
  admin_user_id: int | None,
  plan_uid: int | None,
) -> Tenant:
  name = get_tenant_name()
  length = rng.choices(
    population=TENANT_DESCRIPTION_LENGTHS['population'],
    weights=TENANT_DESCRIPTION_LENGTHS['weights'],
    k=1,
  )[0]
  description = rng.choice(TENANT_DESCRIPTION_TEMPLATES[length])

  if plan_uid is not None:
    if plan_uid not in PLANS.get_uid_list():
      raise ValueError(f'Invalid plan_uid: {plan_uid}.')
  else:
    plan_uid = rng.choice(PLANS.get_uid_list())

  if admin_user_id is not None:
    if not User.objects.filter(id=admin_user_id).exists():
      raise ValueError('User not found.')
  else:
    admin_user_id = User.objects.order_by('?').first().id

  dto = CreateTenantDTO(
    name=name,
    description=description.format(tenant_name=name),
    user_id=admin_user_id,
    plan_uid=PLANS.FREE.uid,
    months=None,
  )

  with transaction.atomic():
    tenant = create_tenant(dto=dto)

    if plan_uid != PLANS.FREE.uid:
      months = None if plan_uid == PLANS.FREE.uid else rng.randint(3, 24)
      subscribe(
        user_id=admin_user_id,
        tenant_id=tenant.id,
        plan_uid=plan_uid,
        months=months,
      )

  return tenant


