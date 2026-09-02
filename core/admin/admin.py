from django.contrib import admin

from core.admin.custom_user import CustomUserAdmin
from core.admin.tenant import TenantAdmin
from core.admin.tenant_user import TenantUserAdmin
from core.models import (
  Tenant,
  TenantUser,
  User,
)


admin.site.register(Tenant, TenantAdmin)
admin.site.register(TenantUser, TenantUserAdmin)
admin.site.register(User, CustomUserAdmin)
