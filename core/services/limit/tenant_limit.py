from core.constants import PLANS
from core.exceptions import ObjectNotFoundError
from core.models import Tenant, TenantLimitOverride
from core.services.subscription import get_tenant_plan_uid


def get_tenant_limit_value(tenant: Tenant, limit_key: str) -> int:
  plan_uid = get_tenant_plan_uid(tenant_id=tenant.id)
  plan = PLANS.get_by_uid(uid=plan_uid)
  if plan is None:
    raise ObjectNotFoundError(f'Plan not found. plan_uid={plan_uid}')

  base_limits = plan.get_record_limits()

  if limit_key not in base_limits:
    raise ValueError(f'Unknown limit key: {limit_key}')

  override = (
    TenantLimitOverride.objects
      .filter(tenant_id=tenant.id, limit_key=limit_key)
      .only('value')
      .first()
  )

  return base_limits[limit_key] if override is None else override.value


def get_tenant_limit_value_by_tenant_id(tenant_id: int, limit_key: str) -> int:
  tenant = Tenant.objects.get(id=tenant_id)
  return get_tenant_limit_value(tenant=tenant)
