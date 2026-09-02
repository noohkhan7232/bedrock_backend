from django.contrib import admin


class TenantAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'domain', 'image',
                  'description',)
  list_display_links = list_display
  exclude = ('deleted_at', 'domain',)
  search_fields = ('name', 'domain', 'image',)
  ordering = ('id', 'name', 'domain',)

  def save_model(self, request, obj, form, change):
    if obj.domain is None or obj.domain == '':
      obj.set_domain()
    obj.save()
