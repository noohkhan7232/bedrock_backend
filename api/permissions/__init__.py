from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated as DRFIsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.constants import CONSTANTS
from core.models import UserEulaAgreement
from core.services.subscription import is_enterprise_tenant


class IsAuthenticated(BasePermission):
  message = 'Authentication required.'
  schema_description = 'Requires authenticated user with agreed EULA.'
  schema_auth = {'bearerAuth': []}

  def has_permission(self, request, view):
    if not DRFIsAuthenticated().has_permission(request, view):
      return False

    # DRFIsAuthenticated().has_permission() already checks the lazily
    # populated request.user, so there is no need to resolve user again here.
    agreed_eula = (
      UserEulaAgreement.objects
        .filter(
          user_id=request.user.id,
          eula_version=CONSTANTS.USER_EULA_VERSION,
        )
        .exists()
    )
    if not agreed_eula:
      raise PermissionDenied('User eula is not agreed.')

    return True


class HasValidExternalAPIKey(BasePermission):
  message = 'Valid API key is required.'
  schema_description = 'Requires a valid external API key.'
  schema_auth = {'externalApiKeyAuth': []}

  def has_permission(self, request, view):
    raise NotImplementedError('External API is not implemented yet.')


class IsTenantMember(BasePermission):
  # Keep independent from IsAuthenticated intentionally by inheriting
  # BasePermission instead of IsAuthenticated,
  # so it can be reused across internal/external API views
  # which will require different types of authentication/authorization.

  message = 'Tenant membership required.'
  schema_description = 'Requires tenant membership.'

  def has_permission(self, request, view):
    # request.tenant_user is populated by TenantContextMiddleware as
    # SimpleLazyObject. Therefore, checking `request.tenant_user is not None`
    # is not sufficient here, because the lazy wrapper itself exists
    # even when the resolved tenant_user is None.
    # We must evaluate the lazy object and check the resolved value instead.
    # Note: If a `SimpleLazyObject` resolves to `None`, `bool(...)` is `False`.
    tenant_user = getattr(request, 'tenant_user', None)
    return bool(tenant_user)


class IsTenantManager(IsTenantMember):
  message = 'Tenant manager required.'
  schema_description = 'Requires tenant manager or admin role.'

  def has_permission(self, request, view):
    if not super().has_permission(request=request, view=view):
      return False

    # Resolve the lazily populated tenant_user explicitly.
    tenant_user = request.tenant_user
    return tenant_user.is_manager or tenant_user.is_admin


class IsTenantAdmin(IsTenantMember):
  message = 'Tenant admin required.'
  schema_description = 'Requires tenant admin role.'

  def has_permission(self, request, view):
    if not super().has_permission(request=request, view=view):
      return False

    # Resolve the lazily populated tenant_user explicitly.
    tenant_user = request.tenant_user
    return tenant_user.is_admin


class IsEnterprise(IsTenantMember):
  message = 'Enterprise tenant required.'
  schema_description = 'Requires enterprise tenant plan.'

  def has_permission(self, request, view):
    if not super().has_permission(request=request, view=view):
      return False

    # Resolve the lazily populated tenant explicitly.
    # Note: If a `SimpleLazyObject` resolves to `None`, `bool(...)` is `False`.
    tenant = request.tenant
    return bool(tenant) and is_enterprise_tenant(tenant=tenant)
