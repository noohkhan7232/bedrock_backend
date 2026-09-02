from dataclasses import dataclass, fields
from typing import Final, Optional

from core.models.choices import TenantLimitKey


USER_EULA_VERSION: Final = '1.0.0'

def get_uid_choices(const_instance, label_attr='name'):
  return [
    (member.uid, getattr(member, label_attr))
    for member in vars(const_instance).values()
    if hasattr(member, 'uid') and hasattr(member, label_attr)
  ]


@dataclass(frozen=True)
class GeneralConstant:
  @classmethod
  def get_value(cls, key, raise_exception=False):
    if not hasattr(cls, key):
      if raise_exception:
        raise KeyError(f"'{key}' is not a valid key in {cls.__name__}.")
      else:
        return None
    return getattr(cls, key)

  @classmethod
  def has_key(cls, key):
    return key in {field.name for field in fields(cls)}

  def as_dict(self, drops=[]):
    return { key: value for key, value in vars(self).items() if key not in drops }

  def as_list(self, as_dict=False, drops=[]):
    return [
      var.as_dict(drops=drops) if as_dict else var
      for _, var in self.as_dict().items()
    ]


@dataclass(frozen=True)
class PeriodConstant:
  SECONDS: Optional[int] = None
  MINUTES: Optional[int] = None
  HOURS: Optional[int] = None
  DAYS: Optional[int] = None
  MONTHS: Optional[int] = None
  YEARS: Optional[int] = None

"""
Contacts
"""
@dataclass(frozen=True)
class _Contacts(GeneralConstant):
  SALES_CONTACT: str = 'support@bedrock.com'
  SUPPORT_CONTACT: str = 'support@bedrock.com'
  API_SUPPORT_CONTACT: str = 'support@bedrock.com'
  HELP_CENTER_URL: str = 'https://example.com/help'
  LANDING_PAGE_URL: str = 'https://example.com'
  TERMS_OF_SERVICE_URL: str = 'https://example.com/terms'
  PRIVACY_POLICY_URL: str = 'https://example.com/privacy'
  CALIFORNIA_NOTICE_URL: str = 'https://example.com/privacy/california-notice'
  SERVICE_OWNER_ADDRESS: str = (
    'Example Company, 123 Example Street, Example City, EX 00000, USA'
  )

"""
System users
"""
@dataclass(frozen=True)
class _SystemUsers(GeneralConstant):
  SYSTEM: str = 'system'
  ANONYMOUS: str = 'anonymous'

SYSTEM_USERS = _SystemUsers()


@dataclass(frozen=True)
class _Constants(GeneralConstant):
  CONTACTS: _Contacts = _Contacts()
  DISPLAYED_USERS_LENGTH: int = 3
  EMAIL_BATCH_SIZE: int = 200
  SPREAD_SHEET_FILE_SIZE_MAX: int = 1024 * 1024 # 1MB
  USER_EULA_VERSION: str = '1.0.0'
  USER_PREVIEW_LENGTH: int = 3
  USER_TENANTS_LIMIT: int = 20
  USER_LINKS_LIMIT: int = 3

CONSTANTS = _Constants()

"""
Diagnosis Params
"""
@dataclass(frozen=True)
class _DiagnosisParams(GeneralConstant):
  TENANT_DIAGNOSIS: PeriodConstant = PeriodConstant(DAYS=30)

DIAGNOSIS_PARAMS = _DiagnosisParams()

"""
Email Queue Lifetimes
"""
@dataclass(frozen=True)
class _EmailQueueLifetimes(GeneralConstant):
  TENANT_USER_COEDIT: PeriodConstant = PeriodConstant(DAYS=14)

EMAIL_QUEUE_LIFETIMES = _EmailQueueLifetimes()


"""
File types
"""
@dataclass(frozen=True)
class _FileTypes(GeneralConstant):
  CSV: str = 'text/csv'
  XLS: str = 'application/vnd.ms-excel'
  XLSX: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


FILE_TYPES = _FileTypes()


"""
Plans
"""
@dataclass(frozen=True)
class _Plan(GeneralConstant):
  uid: int
  name: str
  display_order: int
  is_enterprise: bool
  tenant_users_max: int

  def get_record_limits(self):
    return {
      limit_key.value: getattr(self, limit_key.value)
      for limit_key in TenantLimitKey
    }


@dataclass(frozen=True)
class _Plans(GeneralConstant):
  FREE: _Plan = _Plan(
    uid=0,
    name='Freemium',
    display_order=0,
    is_enterprise=False,
    tenant_users_max=50,
  )
  STANDARD: _Plan = _Plan(
    uid=10,
    name='Standard',
    display_order=10,
    is_enterprise=False,
    tenant_users_max=100,
  )
  ENTERPRISE: _Plan = _Plan(
    uid=100,
    name='Enterprise',
    display_order=100,
    is_enterprise=True,
    tenant_users_max=1000,
  )

  def get_uid_list(self):
    return [plan.uid for plan in self.as_list()]

  def get_by_uid(self, uid, default=None, raise_exception=False):
    plans = [plan for plan in self.as_list() if plan.uid == uid]
    if not plans and raise_exception:
      raise ValueError(f'Plan not found. uid={uid}')
    return plans[0] if plans else default

  def get_name_by_uid(self, uid, default=None, raise_exception=False):
    plan = self.get_by_uid(
      uid=uid,
      raise_exception=raise_exception,
    )
    if plan is None:
      return default
    return plan.name

PLANS = _Plans()

"""
Tenant User Roles
"""
@dataclass(frozen=True)
class _TenantUserRole(GeneralConstant):
  uid: int
  name: str
  access_level: int


@dataclass(frozen=True)
class _TenantUserRoles(GeneralConstant):
  MEMBER: _TenantUserRole = _TenantUserRole(
    uid=0,
    name='Member',
    access_level=0,
  )
  MANAGER: _TenantUserRole = _TenantUserRole(
    uid=50,
    name='Manager',
    access_level=10,
  )
  ADMIN: _TenantUserRole = _TenantUserRole(
    uid=100,
    name='Admin',
    access_level=100,
  )

  def get_uid_list(self):
    return [role.uid for role in self.as_list()]

TENANT_USER_ROLES = _TenantUserRoles()
