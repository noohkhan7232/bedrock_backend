from django.db import transaction

from core.constants import TENANT_USER_ROLES
from core.dtos.tenant_user import (
  CreateAdminTenantUserDTO,
  CreateInvitedTenantUserDTO,
  DeleteCurrentTenantUserDTO,
  DeleteTenantUserDTO,
  UpdateTenantUserRoleDTO,
)
from core.exceptions import (
  CodeNotFoundError,
  ConflictError,
  DuplicateRecordError,
  ObjectNotFoundError,
  PermissionDeniedError,
  ResourceExpiredError,
)
from core.models import (
  Tenant,
  TenantInvitationCode,
  TenantUser,
  User,
)
from core.services.tenant_email_policy import TenantEmailPolicy
from core.services.tenant_limit_override import ensure_tenant_record_limit
from core.services.user import ensure_user_tenants_limit
from core.utils.clock import get_utc_now
from core.utils.email import ensure_valid_email


def create_invited_tenant_user(dto: CreateInvitedTenantUserDTO) -> TenantUser:
  email = ensure_valid_email(email=dto.email)

  with transaction.atomic():
    try:
      user = User.objects.get(email__iexact=email)
      invitation_code = TenantInvitationCode.objects.get(
        email__iexact=email, invitation_code=dto.invitation_code)
    except User.DoesNotExist:
      raise ObjectNotFoundError('User not found.')
    except TenantInvitationCode.DoesNotExist:
      raise CodeNotFoundError('Invalid invitation code.')

    if get_utc_now() > invitation_code.valid_until:
      raise ResourceExpiredError('Invitation code expired.')

    # Inactive memberships still count as already belonging to the workspace.
    query = TenantUser.objects.filter(
      tenant_id=invitation_code.tenant.id, user_id=user.id)
    if query.exists():
      raise DuplicateRecordError('User already in the workspace.')

    TenantEmailPolicy.enforce_allowed(
      tenant=invitation_code.tenant,
      email=user.email,
    )

    ensure_user_tenants_limit(user_id=user.id, add_count=1)
    ensure_tenant_record_limit(
      model=TenantUser,
      key='tenant_users_max',
      tenant_id=invitation_code.tenant.id,
      add_count=1,
      error_message=(
        'Workspace reached the available limit of users.'
      ),
    )

    tenant_user = TenantUser(
      tenant_id=invitation_code.tenant.id,
      user_id=user.id,
      role_uid=dto.role_uid,
    )
    tenant_user.save()

    query = TenantInvitationCode.objects.filter(
      email__iexact=user.email,
      tenant_id=invitation_code.tenant.id,
    )
    query.delete()

  return tenant_user


def create_admin_tenant_user(dto: CreateAdminTenantUserDTO) -> TenantUser:
  # Use objects: inactive memberships still count
  # as already belonging to the workspace.
  query = TenantUser.objects.filter(user_id=dto.user_id, tenant_id=dto.tenant_id)
  if query.exists():
    raise ValueError(
      f'Tenant user already exists.'
      f'(user_id: {dto.user_id}, tenant_id: {dto.tenant_id})'
    )

  try:
    tenant = Tenant.objects.get(id=dto.tenant_id)
    user = User.objects.get(id=dto.user_id)
  except Tenant.DoesNotExist:
    raise ObjectNotFoundError('Tenant not found.')
  except User.DoesNotExist:
    raise ObjectNotFoundError('User not found.')

  tenant_user = TenantUser(
    tenant_id=tenant.id,
    user_id=user.id,
    role_uid=TENANT_USER_ROLES.ADMIN.uid,
  )
  tenant_user.save()

  return tenant_user


def get_tenant_user_min(tenant_user: TenantUser) -> dict:
  image = tenant_user.user.image
  url = image.url if image is not None and image != '' else None

  return {
    'id': tenant_user.id,
    'role_uid': tenant_user.role_uid,
    'title': tenant_user.title,
    'tenant': {
      'id': tenant_user.tenant.id,
    },
    'user': {
      'id': tenant_user.user.id,
      'first_name': tenant_user.user.first_name,
      'last_name': tenant_user.user.last_name,
      'email': tenant_user.user.email,
      'image': url,
      'headline': tenant_user.user.headline,
    },
  }


def _active_admin_exists(
  tenant_id: int,
  exclude_tenant_user_ids: list[int] | None = None,
) -> bool:
  exclude_ids = exclude_tenant_user_ids or []

  return (
    TenantUser.available
      .filter(tenant_id=tenant_id, role_uid=TENANT_USER_ROLES.ADMIN.uid)
      .exclude(id__in=exclude_ids)
      .exists()
  )


def delete_current_tenant_user(dto: DeleteCurrentTenantUserDTO) -> None:
  with transaction.atomic():
    try:
      tenant_user = TenantUser.available.get(id=dto.actor_tenant_user_id)
    except TenantUser.DoesNotExist:
      raise ObjectNotFoundError('Tenant user not found.')

    if tenant_user.is_admin:
      if not _active_admin_exists(
        tenant_id=tenant_user.tenant.id,
        exclude_tenant_user_ids=[tenant_user.id],
      ):
        raise ConflictError(
          'You are the only active admin of the workspace. '
          'Please assign another admin before proceeding.'
        )

    tenant_user.delete()


def delete_tenant_user(dto: DeleteTenantUserDTO) -> None:
  with transaction.atomic():
    try:
      actor = (
        TenantUser.available
          .get(
            id=dto.actor_tenant_user_id,
            role_uid=TENANT_USER_ROLES.ADMIN.uid,
          )
      )
      target = TenantUser.available.get(id=dto.target_tenant_user_id)
    except TenantUser.DoesNotExist:
      raise ObjectNotFoundError('Tenant user not found.')

    if actor.tenant.id != target.tenant.id:
      raise PermissionDeniedError('Can\'t delete other tenant user.')

    if target.is_admin and not _active_admin_exists(
      tenant_id=target.tenant.id,
      exclude_tenant_user_ids=[target.id],
    ):
      raise ConflictError(
        'If the user is deleted, no other admin user is in the tenant. '\
        'Assign other user(s) to admin before proceeding.'
      )

    target.delete()


def update_tenant_user_role(dto: UpdateTenantUserRoleDTO) -> TenantUser:
  with transaction.atomic():
    actor = (
      TenantUser.available.filter(id=dto.actor_tenant_user_id).first()
    )
    if actor is None:
      raise ObjectNotFoundError('Actor tenant user not found.')

    target = (
      TenantUser.available.filter(id=dto.target_tenant_user_id).first()
    )
    if target is None:
      raise ObjectNotFoundError('Target tenant user not found.')

    if actor.tenant.id != target.tenant.id:
      raise PermissionDeniedError(
        'Actor and target must belong to the same tenant.'
      )

    if not actor.is_admin:
      raise PermissionDeniedError('Only active admin can edit role.')

    valid_role_uids = [role.uid for role in TENANT_USER_ROLES.as_list()]
    if dto.role_uid not in valid_role_uids:
      raise PermissionDeniedError('Invalid role_uid.')

    is_self_update = actor.id == target.id
    is_losing_admin = (
      target.role_uid == TENANT_USER_ROLES.ADMIN.uid
      and dto.role_uid != TENANT_USER_ROLES.ADMIN.uid
    )

    if is_self_update and is_losing_admin:
      if not _active_admin_exists(
        tenant_id=actor.tenant.id,
        exclude_tenant_user_ids=[actor.id],
      ):
        raise ConflictError(
          'You are the only active admin of the workspace. '
          'Please assign another admin before proceeding.'
        )

    target.role_uid = dto.role_uid
    target.save(update_fields=['role_uid', 'updated_at'])
    return target
