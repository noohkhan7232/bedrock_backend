from typing import TypedDict

from core.constants import (
  PLANS,
  TENANT_EMAIL_DEFAULT_POLICIES,
  TENANT_USER_ROLES,
)
from core.constants.language import APP_LANGUAGES, LANGUAGE_PROFICIENCIES
from core.constants.timezone import APP_TIMEZONES


class LanguageItem(TypedDict):
  code: str
  display_name: str


class LanguageProficiencyItem(TypedDict):
  uid: int
  name: str
  level: int
  display_order: int


class PlanItem(TypedDict):
  uid: int
  name: str
  display_order: int
  is_enterprise: bool


class TenantEmailDefaultPolicyItem(TypedDict):
  uid: int
  name: str
  display_order: int


class TenantUserRoleItem(TypedDict):
  uid: int
  name: str
  access_level: int


class TimezoneItem(TypedDict):
  coordinate: str
  country_code: str
  code: str
  status: str
  utc_offset: str
  utc_dst_offset: str


class ShareResponseItem(TypedDict):
  languages: list[LanguageItem]
  language_proficiencies: list[LanguageProficiencyItem]
  plans: list[PlanItem]
  tenant_email_default_policies: list[TenantEmailDefaultPolicyItem]
  tenant_user_roles: list[TenantUserRoleItem]
  timezones: list[TimezoneItem]


def get_share() -> ShareResponseItem:
  languages: list[LanguageItem] = [
    {
      'code': item['code'],
      'display_name': item['display_name'],
    }
    for item in APP_LANGUAGES
  ]

  language_proficiencies: list[LanguageProficiencyItem] = [
    {
      'uid': item.uid,
      'name': item.name,
      'level': item.level,
      'display_order': item.display_order,
    }
    for item in LANGUAGE_PROFICIENCIES.as_list()
  ]

  plans: list[PlanItem] = [
    {
      'uid': item['uid'],
      'name': item['name'],
      'display_order': item['display_order'],
      'is_enterprise': item['is_enterprise'],
    }
    for item in PLANS.as_list(as_dict=True)
  ]

  tenant_email_default_policies: list[TenantEmailDefaultPolicyItem] = [
    {
      'uid': item.uid,
      'name': item.name,
      'display_order': item.display_order,
    }
    for item in TENANT_EMAIL_DEFAULT_POLICIES.as_list()
  ]

  tenant_user_roles: list[TenantUserRoleItem] = [
    {
      'uid': item.uid,
      'name': item.name,
      'access_level': item.access_level,
    }
    for item in TENANT_USER_ROLES.as_list()
  ]

  timezones: list[TimezoneItem] = [
    {
      'coordinate': item['coordinate'],
      'country_code': item['country_code'],
      'code': item['code'],
      'status': item['status'],
      'utc_offset': item['utc_offset'],
      'utc_dst_offset': item['utc_dst_offset'],
    }
    for item in APP_TIMEZONES
  ]

  return {
    'languages': languages,
    'language_proficiencies': language_proficiencies,
    'plans': plans,
    'tenant_email_default_policies': tenant_email_default_policies,
    'tenant_user_roles': tenant_user_roles,
    'timezones': timezones,
  }
