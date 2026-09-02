from django.conf import settings
from django.db import transaction

from core.constants import PLANS, TENANT_USER_ROLES
from core.dtos.tenant import (
  CreateTenantDTO,
  CreateTenantDeletionRecordDTO,
  DeleteTenantDTO,
)
from core.dtos.tenant_user import CreateAdminTenantUserDTO
from core.exceptions import DomainValidationError, ObjectNotFoundError
from core.models import Tenant, TenantDeletionRecord, TenantUser
from core.services.subscription import subscribe
from core.services.user import ensure_user_tenants_limit
from core.services.tenant_user import (
  create_admin_tenant_user,
)
from core.utils.clock import get_utc_now
from core.utils.text import generate_random_letters


def create_tenant(dto: CreateTenantDTO) -> Tenant:
  ensure_user_tenants_limit(user_id=dto.user_id)

  if dto.plan_uid != PLANS.FREE.uid:
    raise DomainValidationError(
      'Non-free plan is not configured through API currently. '
      'Contact service provider.'
    )

  with transaction.atomic():
    tenant = Tenant.objects.create(
      name=dto.name,
      description=dto.description,
      domain=generate_random_letters(length=settings.TENANT_DOMAIN_LENGTH),
      account_id=generate_random_letters(length=settings.TENANT_ACCOUNT_ID_LENGTH),
    )
    dto_admin = CreateAdminTenantUserDTO(user_id=dto.user_id, tenant_id=tenant.id)
    create_admin_tenant_user(dto=dto_admin)

    subscribe(
      tenant_id=tenant.id,
      user_id=dto.user_id,
      plan_uid=dto.plan_uid,
      months=dto.months,
    )

  return tenant


def _create_tenant_deletion_record(
  tenant_user: TenantUser,
  deletion_date,
) -> TenantDeletionRecord:
  tenant = tenant_user.tenant
  dto = CreateTenantDeletionRecordDTO(
    tenant_id=tenant.id,
    tenant_name=tenant.name,
    tenant_domain=tenant.domain,
    tenant_account_id=tenant.account_id,
    tenant_description=tenant.description[:1000],
    deletion_date=deletion_date,
  )
  obj = TenantDeletionRecord(**dto.model_dump())
  obj.stamp_created_by(tenant_user=tenant_user)
  obj.save()
  return obj


def delete_tenant(dto: DeleteTenantDTO) -> None:
  with transaction.atomic():
    try:
      deletion_date = get_utc_now()
      tenant = Tenant.objects.get(id=dto.tenant_id, deleted_at__isnull=True)
      tenant_user = TenantUser.available.get(
        tenant_id=tenant.id,
        user_id=dto.user_id,
        role_uid=TENANT_USER_ROLES.ADMIN.uid,
      )
    except Tenant.DoesNotExist:
      raise ObjectNotFoundError('Tenant not found.')
    except TenantUser.DoesNotExist:
      raise ObjectNotFoundError('Tenant user not found.')

    tenant.deleted_at = deletion_date
    tenant.save()

    _create_tenant_deletion_record(
      tenant_user=tenant_user,
      deletion_date=deletion_date,
    )


def get_tenant_admins(
  tenant_id: int,
  max_length: int = 3,
) -> list[TenantUser]:
  admins = (
    TenantUser.available
      .filter(
        tenant_id=tenant_id,
        role_uid=TENANT_USER_ROLES.ADMIN.uid
      )[:max_length]
  )
  return admins.all()


def get_tenant_user_count(tenant_id: int) -> int:
  # User objects: Count inactive tenant users as well.
  return TenantUser.objects.filter(tenant_id=tenant_id).count()
