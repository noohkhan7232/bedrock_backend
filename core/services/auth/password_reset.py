from typing import Any

from django.db import transaction

from core.dtos.auth.password_reset import (
  ResetPasswordDTO,
  SendPasswordResetCodeDTO,
  GetEmailFromCodeDTO,
)
from core.exceptions import (
  DomainValidationError,
  PermissionDeniedError,
)
from core.models import PasswordResetCode, User
from core.services.email.jobs.password_reset import (
  send_password_reset_email,
)
from core.services.sso import is_sso_email
from core.utils.clock import get_utc_now, is_expired
from core.utils.email import ensure_valid_email


def _ensure_valid_non_sso_email(email: str) -> str:
  ensured_email = ensure_valid_email(email=email)

  if is_sso_email(email=ensured_email):
    raise PermissionDeniedError(
      'Single Sign-On users can\'t reset password.'
    )

  return ensured_email


def _delete_password_reset_codes(email: str) -> None:
  query = PasswordResetCode.objects.filter(email__iexact=email)
  query.delete()


def send_password_reset_code(
  dto: SendPasswordResetCodeDTO,
) -> dict[str, Any]:
  result = { 'email_sent': False, 'message': '' }
  ensured_email = _ensure_valid_non_sso_email(email=dto.email)

  if is_sso_email(email=ensured_email):
    raise PermissionDeniedError(
      'Single Sign-On users can\'t reset password.'
    )

  try:
    with transaction.atomic():
      User.objects.get(email__iexact=ensured_email)

      reset_code = PasswordResetCode(email=ensured_email)
      reset_code.set_reset_code()
      reset_code.save()

      send_password_reset_email(
        email=ensured_email,
        reset_code=reset_code.reset_code,
      )

      result['email_sent'] = True
  except User.DoesNotExist:
    pass
  except Exception as e:
    result['message'] = str(e)

  return result


def reset_password(
  dto: ResetPasswordDTO,
) -> dict[str, Any]:
  result = { 'success': False, 'message': '' }
  ensured_email = _ensure_valid_non_sso_email(email=dto.email)

  try:
    with transaction.atomic():
      code = PasswordResetCode.objects.get(
        email__iexact=ensured_email,
        reset_code=dto.reset_code,
      )

      if get_utc_now() > code.valid_until:
        result['message'] = 'Password reset link has expired.'
        raise Exception

      user = User.objects.get(email__iexact=ensured_email)
      user.set_password(dto.password)
      user.save()

      _delete_password_reset_codes(email=user.email)

      result['success'] = True
  except PasswordResetCode.DoesNotExist:
    result['message'] = 'Password reset code not found.'
  except User.DoesNotExist:
    result['message'] = 'Email is not used.'
  except Exception:
    pass

  return result


def get_email_from_code(
  dto: GetEmailFromCodeDTO,
) -> dict[str, Any]:
  result = { 'email': '', 'message': '' }
  try:
    code = PasswordResetCode.objects.get(reset_code=dto.reset_code)
    is_expired(obj=code, key='valid_until', raise_exception=True)
    result['email'] = code.email
  except PasswordResetCode.DoesNotExist:
    raise DomainValidationError('Invalid reset code.')
  except Exception:
    raise

  return result
