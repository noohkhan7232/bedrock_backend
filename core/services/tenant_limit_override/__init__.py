from core.constants import CONSTANTS, PLANS
from core.exceptions import UsageLimitExceededError
from core.models import (
  Tenant,
  TenantLimitOverride,
  TenantUser,
)
from core.services.subscription import get_tenant_plan_uid


def override_tenant_limit(
  tenant_id: int,
  limit_key: str,
  value: int,
) -> TenantLimitOverride:
  """
  Note:
    Records must be explicitly created for values inserted via this command,
    even if they equal the Plan's default value. This locks in the value,
    preventing the tenant's limit_key from unintentionally changing
    if the Plan's default is updated in the future.
  """
  if limit_key not in TenantLimitOverride.LimitKey.values:
    raise ValueError(f'Invalid limit_key: {limit_key}')

  if value < 0:
    raise ValueError('Limit value must be >= 0.')

  if not Tenant.objects.filter(id=tenant_id).exists():
    raise ValueError('Tenant not found.')

  override, _ = TenantLimitOverride.objects.update_or_create(
    tenant_id=tenant_id,
    limit_key=limit_key,
    defaults={
      'value': value,
    },
  )
  return override


def reset_tenant_limit(tenant_id: int, limit_key: str) -> bool:
  if limit_key not in TenantLimitOverride.LimitKey.values:
    raise ValueError(f'Invalid limit_key: {limit_key}')

  override = TenantLimitOverride.objects.filter(
    tenant_id=tenant_id,
    limit_key=limit_key,
  ).first()

  if not override:
    return False

  override.delete()
  return True


def get_tenant_record_limit(
  tenant_id: int,
  raise_exception: bool = True,
) -> dict | None:
  try:
    tenant = Tenant.objects.get(id=tenant_id)
    plan_uid = get_tenant_plan_uid(tenant_id=tenant.id)
    plan = PLANS.get_by_uid(uid=plan_uid, raise_exception=True)
  except Tenant.DoesNotExist:
    if raise_exception:
      raise ValueError('Tenant not found.')
    return None
  except Exception:
    if raise_exception:
      raise
    return None

  record_limit = {
    'tenant_id': tenant.id,
    **plan.get_record_limits(),
  }

  overrides = (
    TenantLimitOverride.objects
      .filter(tenant_id=tenant.id)
      .only('limit_key', 'value')
  )
  for override in overrides:
    record_limit[override.limit_key] = override.value

  return record_limit


def ensure_tenant_record_limit(
  model,
  key: str,
  tenant_id,
  add_count: int = 0,
  error_message: str | None = None,
) -> dict:
  query = model.objects.filter(tenant_id=tenant_id)
  limit = get_tenant_record_limit(tenant_id=tenant_id)
  count = query.count() + add_count
  if count > limit[key]:
    error_message = (
      'Record '
      + 'reaches ' if add_count > 0 else 'reached '
      + 'the available limit of the workspace.'
    ) if not error_message else error_message
    raise UsageLimitExceededError(error_message)
  return dict(count=count, limit=limit[key])
