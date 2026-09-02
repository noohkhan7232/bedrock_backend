from django.db import IntegrityError

from core.dtos.sso import CreateSSOEmailDomainDTO
from core.exceptions import ConflictError
from core.models import SSOEmailDomain
from core.utils.email import get_email_domain


def create_sso_email_domain(dto: CreateSSOEmailDomainDTO) -> SSOEmailDomain:
  try:
    sso_email_domain = SSOEmailDomain(
      domain=dto.domain,
      connection_id=dto.connection_id,
    )
    sso_email_domain.save()
  except IntegrityError as e:
    raise ConflictError(
      f'{dto.domain} is already associated with SSO.'
    ) from e


def is_sso_email(email: str) -> str:
  domain = get_email_domain(email=email)
  query = SSOEmailDomain.objects.filter(domain__iexact=domain)
  return query.exists()
