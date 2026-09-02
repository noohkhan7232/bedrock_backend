from core.constants import TENANT_EMAIL_DEFAULT_POLICIES
from core.exceptions import PermissionDeniedError
from core.models import (
  TenantBlacklistedEmailDomain,
  TenantEmailPolicyConfig,
  TenantWhitelistedEmail,
  TenantWhitelistedEmailDomain,
)
from core.services.tenant_email_policy.rules import domain_matches
from core.utils.email import ensure_valid_email, get_email_domain


class TenantEmailPolicy:
  @staticmethod
  def is_allowed(tenant, email: str) -> bool:
    try:
      email = ensure_valid_email(email).lower()
      domain = get_email_domain(email).lower()
    except ValueError:
      return False

    # Blacklists win; only email-level whitelist may override if enabled.
    allow_all, email_whitelist_overrides_blacklist = (
      TenantEmailPolicy.get_default_policy(tenant)
    )

    blacklisted_email_domain_rules = (
      TenantEmailPolicy.get_blacklisted_email_domain_rules(tenant)
    )
    whitelisted_email_domain_rules = (
      TenantEmailPolicy.get_whitelisted_email_domain_rules(tenant)
    )
    whitelisted_email_set = (
      TenantEmailPolicy.get_whitelisted_email_set(tenant)
    )
    email_is_whitelisted = email in whitelisted_email_set

    if email_whitelist_overrides_blacklist and email_is_whitelisted:
      return True

    if domain_matches(domain, blacklisted_email_domain_rules):
      return False

    if email_is_whitelisted:
      return True

    if not whitelisted_email_domain_rules:
      return allow_all

    return (
      domain_matches(domain, whitelisted_email_domain_rules)
    )

  @staticmethod
  def enforce_allowed(tenant, email: str) -> None:
    if not TenantEmailPolicy.is_allowed(tenant, email):
      raise PermissionDeniedError('Email is not allowed by the tenant policy.')

  @staticmethod
  def get_default_policy(tenant):
    allow_all = True
    email_whitelist_overrides_blacklist = False

    query = TenantEmailPolicyConfig.objects.filter(tenant_id=tenant.id)
    if query.exists():
      obj = query.first()
      allow_all = (
        obj.default_policy_uid == TENANT_EMAIL_DEFAULT_POLICIES.ALLOW_ALL.uid
      )
      email_whitelist_overrides_blacklist = (
        obj.email_whitelist_overrides_blacklist
      )

    return allow_all, email_whitelist_overrides_blacklist

  @staticmethod
  def get_whitelisted_email_set(tenant):
    query = (
      TenantWhitelistedEmail.objects
        .filter(tenant_id=tenant.id)
        .values_list('email', flat=True)
    )
    return {email.lower() for email in query}

  @staticmethod
  def get_blacklisted_email_domain_rules(tenant):
    query = (
      TenantBlacklistedEmailDomain.objects
        .filter(tenant_id=tenant.id)
        .values_list('domain', 'include_subdomains')
    )
    return [
      (domain.lower(), bool(include_subdomains))
      for domain, include_subdomains in query
    ]

  @staticmethod
  def get_whitelisted_email_domain_rules(tenant):
    query = (
      TenantWhitelistedEmailDomain.objects
        .filter(tenant_id=tenant.id)
        .values_list('domain', 'include_subdomains')
    )
    return [
      (domain.lower(), bool(include_subdomains))
      for domain, include_subdomains in query
    ]


def get_tenant_email_policy_config(
  tenant_id: int,
  raise_exception: bool = False,
) -> TenantEmailPolicyConfig | None:
  try:
    return (
      TenantEmailPolicyConfig.objects
        .filter(tenant_id=tenant_id)
        .get()
    )
  except TenantEmailPolicyConfig.DoesNotExist:
    if raise_exception:
      raise

  return None


def get_tenant_blacklisted_email_domains(
  tenant_id: int,
  raise_exception: bool = False,
) -> list[TenantBlacklistedEmailDomain]:
  try:
    return (
      TenantBlacklistedEmailDomain.objects
        .filter(tenant_id=tenant_id)
        .all()
    )
  except TenantBlacklistedEmailDomain.DoesNotExist:
    if raise_exception:
      raise

  return []


def get_tenant_whitelisted_email_domains(
  tenant_id: int,
  raise_exception: bool = False,
) -> list[TenantWhitelistedEmailDomain]:
  try:
    return (
      TenantWhitelistedEmailDomain.objects
        .filter(tenant_id=tenant_id)
        .all()
    )
  except TenantWhitelistedEmailDomain.DoesNotExist:
    if raise_exception:
      raise

  return []


def get_tenant_whitelisted_emails(
  tenant_id: int,
  raise_exception: bool = False,
) -> list[TenantWhitelistedEmail]:
  try:
    return (
      TenantWhitelistedEmail.objects
        .filter(tenant_id=tenant_id)
        .all()
    )
  except TenantWhitelistedEmail.DoesNotExist:
    if raise_exception:
      raise

  return []
