from core.dtos.auth.email_verification import (
  GetEmailAvailabilityDTO,
  GetEmailFromCodeDTO,
  IssueEmailVerificationCodeDTO,
)
from core.exceptions import DomainValidationError
from core.models import EmailVerificationCode, User
from core.utils.clock import is_expired
from core.utils.email import ensure_valid_email


def get_email_availability(dto: GetEmailAvailabilityDTO) -> bool:
  ensured_email = ensure_valid_email(dto.email)
  return not User.objects.filter(email__iexact=ensured_email).exists()


def issue_email_verification_code(
  dto: IssueEmailVerificationCodeDTO,
) -> EmailVerificationCode | None:
  ensured_email = ensure_valid_email(email=dto.email)

  try:
    query = User.objects.filter(email__iexact=ensured_email)
    if query.exists():
      return None
    obj = EmailVerificationCode(email=ensured_email)
    obj.set_verification_code()
    obj.save()
    return obj
  except Exception:
    pass

  return None


def get_email_from_code(dto: GetEmailFromCodeDTO) -> str:
  if not dto.verification_code:
    DomainValidationError('Invalid verification code.')

  try:
    obj = (
      EmailVerificationCode.objects.get(verification_code=dto.verification_code)
    )
    is_expired(obj=obj, key='valid_until', raise_exception=True)
    return obj.email
  except EmailVerificationCode.DoesNotExist:
    raise DomainValidationError('Invalid verification code.')
  except Exception:
    raise

