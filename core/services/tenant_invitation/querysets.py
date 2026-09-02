from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import (
  BooleanField,
  Case,
  Exists,
  OuterRef,
  QuerySet,
  Value,
  When,
)

from core.constants import TENANT_USER_ROLES
from core.constants.search import SIMILARITY_THRESH_LOOSE
from core.models import TenantInvitationCode, TenantUser
from core.utils.clock import get_utc_now


def get_tenant_invitation_codes(
  tenant_id: int,
  search: str | None = None,
) -> QuerySet[TenantInvitationCode]:
  query = (
    TenantInvitationCode.objects
      .filter(
        tenant_id=tenant_id,
        valid_until__gt=get_utc_now(),
      )
      .alias(
        email_exists=Exists(
          # Use objects: Inactive memberships should still
          # count as already belonging to tenant.
          TenantUser.objects.filter(
            tenant_id=tenant_id,
            user__email__iexact=OuterRef('email'),
          )
        )
      )
      .filter(email_exists=False)
  )

  if search:
    query = query.annotate(
      is_exact_match=Case(
        When(email__iexact=search, then=Value(True)),
        default=Value(False),
        output_field=BooleanField(),
      )
    ).annotate(
      similarity=TrigramSimilarity('email', search),
    ).filter(
      similarity__gt=SIMILARITY_THRESH_LOOSE
    ).order_by('-is_exact_match', '-similarity')

  return query


def get_current_user_tenant_invitation_codes(
  email: str,
):
  query = (
    TenantInvitationCode.objects
      .filter(
        tenant__deleted_at__isnull=True,
        email__iexact=email,
        valid_until__gt=get_utc_now(),
      )
      .alias(
        current_user_is_active_tenant_user=Exists(
          TenantUser.available.filter(
            tenant_id=OuterRef('tenant_id'),
            user__email__iexact=email,
          )
        ),
        has_active_admin=Exists(
          TenantUser.available.filter(
            tenant_id=OuterRef('tenant_id'),
            role_uid=TENANT_USER_ROLES.ADMIN.uid,
          )
        ),
      )
      .filter(
        current_user_is_active_tenant_user=False,
        has_active_admin=True,
      )
  )

  return query
