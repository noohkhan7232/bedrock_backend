from types import SimpleNamespace

from core.constants import PLANS, TENANT_USER_ROLES


DEFAULTS = SimpleNamespace(
  PASSWORD='Pa$$w0rd!',
  PLAN='free',
  TENANT_USER_ROLE='member',
)

PLAN_MAP = {
  'free': PLANS.FREE,
  'standard': PLANS.STANDARD,
  'enterprise': PLANS.ENTERPRISE,
}

PLAN_UID_MAP = {
  value.uid: key for key, value in PLAN_MAP.items()
}

PLANS = tuple(key for key in PLAN_MAP.keys())

TENANT_USER_ROLE_MAP = {
  'admin': TENANT_USER_ROLES.ADMIN,
  'manager': TENANT_USER_ROLES.MANAGER,
  'member': TENANT_USER_ROLES.MEMBER,
}

TENANT_USER_ROLE_UID_MAP = {
  value.uid: key for key, value in TENANT_USER_ROLE_MAP.items()
}

TENANT_USER_ROLES = tuple(key for key in TENANT_USER_ROLE_MAP.items())

TENANT_EMAIL_DEFAULT_POLICIES = SimpleNamespace(
  ALLOW_ALL=SimpleNamespace(uid=1),
  DENY_UNLISTED=SimpleNamespace(uid=2),
)
