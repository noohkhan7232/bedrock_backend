from django.conf import settings

from core.dtos.auth.sso import (
  GetSsoAuthorizationUrlDTO,
  GetSsoEnabledDTO,
)
from core.exceptions import DomainValidationError
from core.models import SSOEmailDomain
from core.services.auth.workos import workos_client
from core.utils.email import (
  dict_to_url_params,
  ensure_valid_email,
  ensure_valid_email_domain,
  get_email_domain,
)


def get_authorization_url(dto: GetSsoAuthorizationUrlDTO) -> str:
  ensured_email = ensure_valid_email(email=dto.email)
  email_domain = get_email_domain(email=ensured_email)
  if not email_domain:
    raise DomainValidationError('Email domain not found.')

  try:
    obj = SSOEmailDomain.objects.get(domain__iexact=email_domain)
    state = dict_to_url_params({
      'email': ensured_email,
      'invitation_code': dto.invitation_code,
      'verification_code': dto.verification_code,
    })
    authorization_url = workos_client.sso.get_authorization_url(
      connection=obj.connection_id,
      redirect_uri=settings.SSO_REDIRECT_URI,
      state=state,
    )
    return authorization_url
  except SSOEmailDomain.DoesNotExist:
    return ''


def get_sso_enabled(dto: GetSsoEnabledDTO) -> bool:
  ensured_email_domain = ensure_valid_email_domain(dto.email_domain)
  ensured_email_domain = ensured_email_domain.replace('@', '')

  return (
    SSOEmailDomain.objects
      .filter(domain__iexact=ensured_email_domain)
      .exists()
  )
