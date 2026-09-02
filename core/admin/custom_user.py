from django.contrib.auth.admin import UserAdmin

from core import forms


class CustomUserAdmin(UserAdmin):
  fieldsets = (
    (None, {'fields': ('first_name', 'last_name', 'email', 'password', 'image',
                       'status', 'headline', 'location', 'locale', 'timezone_code',
                       'disable_promotion',)}),
  )
  add_fieldsets = (
      (None, {
        'classes': ('wide',),
        'fields': ('first_name', 'last_name', 'email', 'password1', 'password2',
                   'image', 'status', 'headline', 'location', 'locale',
                   'timezone_code', 'disable_promotion',),
      }),
  )
  form = forms.CustomUserChangeForm
  add_form = forms.CustomUserCreationForm
  list_display = ('id', 'first_name', 'last_name', 'email', 'image',
                  'status', 'headline', 'location', 'locale',
                  'timezone_code', 'disable_promotion', 'is_staff',)
  list_display_links = list_display
  search_fields = ('first_name', 'last_name', 'email',)
  ordering = ('id', 'email',)
