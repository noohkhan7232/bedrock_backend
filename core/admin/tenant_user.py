from django.contrib import admin


class TenantUserAdmin(admin.ModelAdmin):
  list_display = ('id', 'tenant_id', 'user_id', 'role_uid',
                  'disable_email_notification',)
  list_display_links = list_display
  exclude = ('deleted_at',)
  search_fields = ('tenant_id', 'name', 'user_id', 'role_uid',)
  ordering = ('id', 'tenant_id', 'user_id',)
