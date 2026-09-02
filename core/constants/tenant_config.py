from dataclasses import dataclass

from core.constants import GeneralConstant


@dataclass(frozen=True)
class _TenantEmailDefaultPolicy(GeneralConstant):
  uid: int
  name: str
  display_order: int


@dataclass(frozen=True)
class _TenantEmailDefaultPolicies(GeneralConstant):
  ALLOW_ALL: _TenantEmailDefaultPolicy = _TenantEmailDefaultPolicy(
    uid=1,
    name='Allow all email domains',
    display_order=1,
  )
  DENY_UNLISTED: _TenantEmailDefaultPolicy = _TenantEmailDefaultPolicy(
    uid=2,
    name='Deny unlisted email domains',
    display_order=2,
  )

  def get_uid_list(self):
    return [policy.uid for policy in self.as_list()]

TENANT_EMAIL_DEFAULT_POLICIES = _TenantEmailDefaultPolicies()
