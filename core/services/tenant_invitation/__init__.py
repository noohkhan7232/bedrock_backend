import datetime

from django.db import transaction, IntegrityError

from core.constants import TENANT_USER_ROLES
from core.dtos.tenant_invitation import (
  AcceptTenantInvitationDTO,
  DeclineTenantInvitationDTO,
  GetEmailFromCodeDTO,
  GetTenantFromCodeDTO,
  InviteToTenantDTO,
)
from core.dtos.tenant_user import CreateInvitedTenantUserDTO
from core.exceptions import (
  DomainValidationError,
  DuplicateRecordError,
  ObjectNotFoundError,
)
from core.models import (
  TenantInvitationCode,
  Tenant,
  TenantUser,
  User,
)
from core.services.tenant_email_policy import TenantEmailPolicy
from core.services.tenant_limit_override import ensure_tenant_record_limit
from core.services.tenant_user import create_invited_tenant_user
from core.utils.clock import get_utc_now, is_expired
from core.utils.email import ensure_valid_email


def _ensure_record_limit(tenant_id: int, add_count: int) -> None:
  ensure_tenant_record_limit(
    model=TenantUser,
    key='tenant_users_max',
    tenant_id=tenant_id,
    add_count=add_count,
    error_message='Workspace reached the available limit of users.',
  )


def _ensure_no_existing_tenant_users(
  tenant_id: int,
  emails: list[str],
) -> None:
  # Use objects, not available: inactive-but-alive memberships must still
  # block duplcate invitations.
  query = (
    TenantUser.objects
      .filter(tenant_id=tenant_id, user__email__in=emails)
  )

  if query.exists():
    found_emails = [obj.user.email for obj in query.all()]
    found_emails_str = (
      f"{', '.join(found_emails)} are "
      if len(found_emails) > 1 else f'{found_emails[0]} is '
    )
    raise DuplicateRecordError(
      f'{found_emails_str} already in workspace.'
    )


def _ensure_email_policy(tenant: Tenant, email: str) -> None:
  TenantEmailPolicy.enforce_allowed(tenant=tenant, email=email)


def _delete_expired_invitation_codes(
  tenant_id: int,
  emails: list[str],
  now: datetime.datetime,
) -> None:
  TenantInvitationCode.objects.filter(
    tenant_id=tenant_id,
    email__in=emails,
    valid_until__lt=now,
  ).delete()


def _upsert_tenant_invitation_code(
  tenant_id: int,
  tenant_user_id: int,
  email: str,
  now: datetime.datetime,
) -> TenantInvitationCode:
  obj = (
    TenantInvitationCode.objects
      .select_for_update(of=('self',))
      .filter(tenant_id=tenant_id, email__iexact=email)
      .order_by('-valid_until')
      .first()
  )

  if obj:
    obj.issue_invitation(tenant_user_id=tenant_user_id)
    obj.save(update_fields=[
      'invitation_code',
      'invited_at',
      'valid_until',
      'invited_by',
    ])
    return obj

  try:
    obj = TenantInvitationCode(tenant_id=tenant_id, email=email)
    obj.issue_invitation(tenant_user_id=tenant_user_id)
    obj.save()
    return obj
  except IntegrityError: # Created just now elsewhere, etc.
    obj = (
      TenantInvitationCode.objects
        .select_for_update(of=('self',))
        .filter(tenant_id=tenant_id, email__iexact=email)
        .order_by('-valid_until')
        .first()
    )
    if not obj:
      raise
    obj.issue_invitation(tenant_user_id=tenant_user_id)
    obj.save(update_fields=[
      'invitation_code',
      'invited_at',
      'valid_until',
      'invited_by',
    ])
    return obj


def _delete_invitations(
  tenant_id: int,
  email: str,
) -> None:
  query = (
    TenantInvitationCode.objects.filter(tenant_id=tenant_id, email__iexact=email)
  )
  query.delete()


def invite_to_tenant(
  dto: InviteToTenantDTO,
) -> list[TenantInvitationCode]:
  try:
    emails = list({
      ensure_valid_email(email=email)
      for email in dto.emails
    })
    _ensure_record_limit(tenant_id=dto.tenant_id, add_count=len(emails))
    _ensure_no_existing_tenant_users(
      tenant_id=dto.tenant_id,
      emails=emails,
    )

    tenant = Tenant.objects.get(id=dto.tenant_id)
    for email in emails:
      _ensure_email_policy(tenant=tenant, email=email)

    TenantUser.available.get(
      id=dto.tenant_user_id, tenant_id=dto.tenant_id)
    now = get_utc_now()

    with transaction.atomic():
      _delete_expired_invitation_codes(
        tenant_id=dto.tenant_id,
        emails=emails,
        now=now,
      )

      tenant_invitation_codes = []
      for email in emails:
        tenant_invitation_code = _upsert_tenant_invitation_code(
          tenant_id=dto.tenant_id,
          tenant_user_id=dto.tenant_user_id,
          email=email,
          now=now,
        )
        tenant_invitation_codes.append(tenant_invitation_code)
    return tenant_invitation_codes
  except Tenant.DoesNotExist:
    raise ObjectNotFoundError('Tenant not found.')
  except TenantUser.DoesNotExist:
    raise ObjectNotFoundError('Tenant user not found.')
  except Exception:
    raise


def accept_invitation(
  dto: AcceptTenantInvitationDTO,
) -> Tenant:
  with transaction.atomic():
    try:
      user = User.objects.get(id=dto.user_id)
      code = TenantInvitationCode.objects.get(
        email__iexact=user.email,
        invitation_code=dto.invitation_code,
      )
      _ensure_record_limit(tenant_id=code.tenant.id, add_count=1)
      _ensure_no_existing_tenant_users(
        tenant_id=code.tenant.id,
        emails=[user.email],
      )
      is_expired(obj=code, key='valid_until', raise_exception=True)
      _ensure_email_policy(tenant=code.tenant, email=user.email)

      dto = CreateInvitedTenantUserDTO(
        email=user.email,
        invitation_code=dto.invitation_code,
        role_uid=TENANT_USER_ROLES.MEMBER.uid,
      )
      create_invited_tenant_user(dto=dto)
      _delete_invitations(tenant_id=code.tenant.id, email=user.email)

      return code.tenant
    except User.DoesNotExist:
      raise ObjectNotFoundError('User not found.')
    except TenantInvitationCode.DoesNotExist:
      raise DomainValidationError('Invalid invitation code.')
    except Exception:
      raise


def decline_invitation(
  dto: DeclineTenantInvitationDTO,
) -> Tenant:
  with transaction.atomic():
    try:
      user = User.objects.get(id=dto.user_id)
      code = TenantInvitationCode.objects.get(
        email__iexact=user.email,
        invitation_code=dto.invitation_code,
      )
      _delete_invitations(tenant_id=code.tenant.id, email=user.email)
      return code.tenant
    except User.DoesNotExist:
      raise ObjectNotFoundError('User not found.')
    except TenantInvitationCode.DoesNotExist:
      raise DomainValidationError('Invalid invitation code.')
    except Exception:
      raise


def get_email_from_code(dto: GetEmailFromCodeDTO) -> str:
  if not dto.invitation_code:
    raise DomainValidationError('Invalid invitation code')

  try:
    obj = TenantInvitationCode.objects.get(
      invitation_code=dto.invitation_code,
    )
    is_expired(obj=obj, key='valid_until', raise_exception=True)
    return obj.email
  except TenantInvitationCode.DoesNotExist:
    raise DomainValidationError('Invalid invitation code.')
  except Exception:
    raise


def get_tenant_from_code(dto: GetTenantFromCodeDTO) -> Tenant:
  if not dto.invitation_code:
    raise DomainValidationError('Invalid invitation code')

  try:
    obj = TenantInvitationCode.objects.get(
      invitation_code=dto.invitation_code,
    )
    is_expired(obj=obj, key='valid_until', raise_exception=True)
    return obj.tenant
  except TenantInvitationCode.DoesNotExist:
    raise DomainValidationError('Invalid invitation code.')
  except Exception:
    raise


def delete_tenant_invitation_codes(
  tenant_id: int,
  tenant_invitation_code_id: int,
) -> None:
  try:
    code = (
      TenantInvitationCode.objects
        .get(
          id=tenant_invitation_code_id,
          tenant_id=tenant_id,
        )
    )
  except TenantInvitationCode.DoesNotExist:
    raise ObjectNotFoundError('Invitation code not found.')

  codes = (
    TenantInvitationCode.objects
      .filter(
        tenant_id=tenant_id,
        email__iexact=code.email,
      )
  )
  codes.delete()
