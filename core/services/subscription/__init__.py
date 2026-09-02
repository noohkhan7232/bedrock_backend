from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.utils import timezone

from core.constants import PLANS, TENANT_USER_ROLES
from core.exceptions import PermissionDeniedError
from core.models import Subscription, Tenant, TenantUser
from core.utils.clock import get_utc_now


def get_tenant_subscription(
  tenant_id: int,
  raise_exception: bool = False,
) -> Subscription | None:
  try:
    return Subscription.objects.get(tenant_id=tenant_id)
  except Subscription.DoesNotExist:
    if raise_exception:
      raise

  return None


def get_tenant_plan_uid(tenant_id: int) -> int:
  subscription = get_tenant_subscription(tenant_id=tenant_id)
  return PLANS.FREE.uid if subscription is None else subscription.plan_uid


def is_enterprise_tenant(tenant: Tenant) -> bool:
  subscription = get_tenant_subscription(tenant_id=tenant.id)

  if subscription is None:
    return False

  if subscription.plan_uid != PLANS.ENTERPRISE.uid:
    return False

  if subscription.expires_at is None:
    return True

  """
  1 day is added to expires_at for margin,
  to simplify issues related to timezone difference.
  """
  return subscription.expires_at + timedelta(days=1) >= timezone.localdate()


def subscribe(
  user_id: int,
  tenant_id: int,
  plan_uid: str,
  months: int | None,
) -> Subscription:
  with transaction.atomic():
    try:
      TenantUser.available.get(
        tenant_id=tenant_id,
        user_id=user_id,
        role_uid=TENANT_USER_ROLES.ADMIN.uid,
      )

      subscribed_at = get_utc_now()
      expires_at = (
        subscribed_at + relativedelta(months=months, days=1)
        if (plan_uid != PLANS.FREE.uid) and (months is not None) else None
      )

      data = {
        'tenant_id': tenant_id,
        'plan_uid': plan_uid,
        'subscribed_at': subscribed_at,
        'expires_at': expires_at,
      }
      Subscription.objects.filter(tenant_id=tenant_id).delete()
      subscription = Subscription.objects.create(**data)
      return subscription
    except TenantUser.DoesNotExist:
      raise PermissionDeniedError('Admin not found.')
