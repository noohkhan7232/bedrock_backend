from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, QuerySet, Value
from django.db.models.functions import Concat, Greatest

from core.constants import TENANT_USER_ROLES
from core.constants.search import (
  EMAIL_SEARCH_MIN_LENGTH,
  SIMILARITY_THRESH_LOOSE,
  SIMILARITY_THRESH_MODERATE,
  USER_SEARCH_MIN_LENGTH,
)
from core.exceptions import DomainValidationError, ObjectNotFoundError
from core.models import TenantUser


def _annotate_name_similarity_by_full_name(
  query: QuerySet[TenantUser],
  search: str,
) -> QuerySet[TenantUser]:
  return (
    query
      .alias(
        username=Concat('user__first_name', Value(' '), 'user__last_name')
      )
      .annotate(
        name_similarity=TrigramSimilarity('username', search)
      )
  )


def _annotate_name_similarity_by_first_or_last_name(
  query: QuerySet[TenantUser],
  search: str,
) -> QuerySet[TenantUser]:
  return (
    query
      .alias(fn_similarity=TrigramSimilarity('user__first_name', search))
      .alias(ln_similarity=TrigramSimilarity('user__last_name', search))
      .annotate(name_similarity=Greatest('fn_similarity', 'ln_similarity'))
  )


def _annotate_name_similarity(
  query: QuerySet[TenantUser],
  search: str,
) -> QuerySet[TenantUser]:
  is_single_word = len(search.split(' ')) == 1
  if is_single_word:
    query = _annotate_name_similarity_by_first_or_last_name(
      query=query,
      search=search,
    )
  else:
    query = _annotate_name_similarity_by_full_name(query=query, search=search)

  return query


def get_tenant_users(
  tenant_id: int,
  role_uid: int | None = None,
  search: str | None = None,
) -> QuerySet[TenantUser]:
  if (
    (role_uid is not None)
    and (role_uid not in TENANT_USER_ROLES.as_uid_list())
  ):
    raise DomainValidationError(f'Invalid role_uid: {role_uid}')

  # Use objects: Show all current memberships
  # in the tenant including inactive ones.
  query = (
    TenantUser.objects.filter(
      tenant_id=tenant_id,
      deleted_at__isnull=True,
    )
  )

  if role_uid is not None:
    query = query.filter(role_uid=role_uid)

  if search:
    search = search.strip()
    query = _annotate_name_similarity(query, search=search)

    cond = Q(name_similarity__gt=SIMILARITY_THRESH_MODERATE)
    if len(search) >= EMAIL_SEARCH_MIN_LENGTH:
      cond |= Q(user__email__icontains=search)

    # TODO: order correctly.
    query = query.filter(cond).order_by('-name_similarity')

  return query


def get_matched_tenant_users(
  actor_tenant_user_id: int,
  search: str,
  include_self: bool = False,
  limit: int = 10,
) -> QuerySet[TenantUser]:
  search = search.strip()

  if len(search) < USER_SEARCH_MIN_LENGTH:
    return TenantUser.objects.none()

  try:
    actor = (
      TenantUser.available
        .only('id', 'tenant_id')
        .get(id=actor_tenant_user_id)
    )
  except TenantUser.DoesNotExist:
    raise ObjectNotFoundError('Tenant user not found.')

  query = TenantUser.available.filter(tenant_id=actor.tenant_id)

  if not include_self:
    query = query.exclude(id=actor.id)

  query = _annotate_name_similarity(query, search=search)

  cond = Q(name_similarity__gt=SIMILARITY_THRESH_LOOSE)
  if len(search) >= EMAIL_SEARCH_MIN_LENGTH:
    cond |= Q(user__email__icontains=search)

  # TODO: order correctly.
  query = query.filter(cond).order_by('-name_similarity')[:limit]

  return query
