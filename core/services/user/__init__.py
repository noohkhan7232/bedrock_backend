from django.db import transaction

from core.constants import CONSTANTS, TENANT_USER_ROLES
from core.dtos.auth.token import GetTokenPairDTO
from core.dtos.user import (
  CreateUserDTO,
  DeleteCurrentUserDTO,
  UpdateUserImageDTO,
  UpdateUserPasswordDTO,
)
from core.exceptions import (
  CodeNotFoundError,
  DomainValidationError,
  PermissionDeniedError,
  ResourceExpiredError,
  SSOAuthenticationError,
  UsageLimitExceededError,
)
from core.models import (
  EmailVerificationCode,
  TenantInvitationCode,
  TenantUser,
  User,
  UserEulaAgreement,
)
from core.services.auth.token import get_token_pair
from core.services.sso import is_sso_email
from core.utils.clock import get_utc_now
from core.utils.email import ensure_valid_email
from core.utils.text import generate_random_letters


def ensure_user_tenants_limit(user_id: int, add_count: int = 0) -> dict:
  # Count only active memberships toward the user tenant limit.
  # Reactivation must enforce this same limit before setting active=True.
  query = TenantUser.available.filter(user_id=user_id)
  limit = CONSTANTS.USER_TENANTS_LIMIT
  count = query.count() + add_count
  if count > limit:
    raise UsageLimitExceededError('Cannot join more tenants; limit reached.')
  return dict(count=count, limit=limit)


def _validate_create_user_dto(dto: CreateUserDTO) -> None:
  ensured_email = ensure_valid_email(email=dto.email)

  if not dto.invitation_code and not dto.verification_code:
    raise ValueError(
      'Either invitation code or verification code is required.'
    )

  if dto.invitation_code:
    query = TenantInvitationCode.objects.filter(
      email__iexact=ensured_email,
      invitation_code=dto.invitation_code,
    )
    if not query.exists():
      raise CodeNotFoundError(
        'Inivitation link is invalid. Please contact workspace admin.'
      )
    if get_utc_now() > query.get().valid_until:
      raise ResourceExpiredError(
        'Invitation link has expired. Please contact workspace admin.'
      )

  if dto.verification_code:
    query = EmailVerificationCode.objects.filter(
      email__iexact=ensured_email,
      verification_code=dto.verification_code,
    )
    if not query.exists():
      raise CodeNotFoundError(
        'Verification link is invalid. Please restart sign-up.'
      )
    if get_utc_now() > query.get().valid_until:
      raise ResourceExpiredError(
        'Verification link has expired. Please restart sign-up.'
      )

  sso = is_sso_email(email=ensured_email)
  if sso and dto.password:
    raise PermissionDeniedError(
      'Single Sign-On users can\'t set password for sign-up.'
    )
  if sso and not dto.sso_code:
    raise SSOAuthenticationError('Sigle Sign-On users need sso_code.')


def _create_user_eula_agreement(user_id: int) -> None:
  UserEulaAgreement.objects.create(
    user_id=user_id,
    eula_version=CONSTANTS.USER_EULA_VERSION,
  )


def _delete_email_verification_codes(email: str) -> None:
  query = EmailVerificationCode.objects.filter(email__iexact=email)
  query.delete()


def create_user(dto: CreateUserDTO) -> tuple[User, dict]:
  _validate_create_user_dto(dto=dto)
  ensured_email = ensure_valid_email(email=dto.email)

  with transaction.atomic():
    user = User(
      email=ensured_email,
      first_name=dto.first_name,
      last_name=dto.last_name,
      headline=dto.headline,
      location=dto.location,
    )
    user.set_password(
      generate_random_letters(length=32)
      if dto.sso_code else dto.password
    )
    user.save()

    dto_token_pair = GetTokenPairDTO(
      **{
        'email': user.email,
        'ip_address': None,
        **({
          'sso_code': dto.sso_code,
        } if dto.sso_code else {
          'password': dto.password,
        }),
      }
    )
    token_pair = get_token_pair(dto=dto_token_pair)

    _create_user_eula_agreement(user_id=user.id)
    _delete_email_verification_codes(email=user.email)

  return user, token_pair.model_dump()


def update_user_image(
  dto: UpdateUserImageDTO,
) -> None:
  with transaction.atomic():
    try:
      user = User.objects.get(id=dto.user_id)
      user.image = dto.image
      user.save()
      return user
    except User.DoesNotExist:
      raise
    except Exception:
      raise


def update_user_password(
  dto: UpdateUserPasswordDTO,
) -> User:
  if dto.password == dto.new_password:
    raise DomainValidationError('New password is the same as current password.')

  with transaction.atomic():
    try:
      user = User.objects.get(id=dto.user_id)
      if not user.check_password(dto.password):
        raise DomainValidationError('Current password is wrong.')
      if is_sso_email(user.email):
        raise DomainValidationError('SSO user can\'t update password.')

      user.set_updater(user)
      user.set_password(dto.new_password)
      user.save()
    except User.DoesNotExist:
      raise DomainValidationError('User not found.')
    except Exception:
      raise


def _user_is_only_admin_in_any_tenant(user_id: int) -> bool:
  query = TenantUser.available.filter(
    user_id=user_id,
    role_uid=TENANT_USER_ROLES.ADMIN.uid,
  )

  for admin in query.all():
    other_admin_exists = (
      TenantUser.available
        .filter(
          tenant_id=admin.tenant.id,
          role_uid=TENANT_USER_ROLES.ADMIN.uid,
        )
        .exclude(user_id=user_id)
        .exists()
    )

    if not other_admin_exists:
      return True

  return False


def delete_current_user(dto: DeleteCurrentUserDTO) -> None:
  try:
    user = User.objects.get(id=dto.actor_user_id)
  except User.DoesNotExist:
    raise DomainValidationError('User not found.')
  except Exception:
    raise

  if _user_is_only_admin_in_any_tenant(user_id=user.id):
    raise PermissionDeniedError(
      'User cannot be deleted because the user is the only admin of a tenant. '
      'Please assign another admin or delete the tenant before proceeding.'
    )

  user.delete()
