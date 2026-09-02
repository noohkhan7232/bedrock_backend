from django.utils.functional import SimpleLazyObject


class TenantContextMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
    return response

  def process_view(self, request, view_func, view_args, view_kwargs):
    domain = view_kwargs.get('domain')

    if not domain:
      return None

    request.tenant = SimpleLazyObject(
      lambda: self._get_tenant(domain)
    )
    request.tenant_user = SimpleLazyObject(
      lambda: self._get_tenant_user(request, domain)
    )

    return None

  def _get_tenant(self, domain):
    from core.models import Tenant

    try:
      return Tenant.objects.get(domain=domain, deleted_at__isnull=True)
    except Tenant.DoesNotExist:
      return None

  def _get_tenant_user(self, request, domain):
    from core.models import TenantUser

    try:
      return TenantUser.available.get(tenant__domain=domain, user=request.user)
    except TenantUser.DoesNotExist:
      return None
