from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from core.models import User


class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = User
    fields = (
      'first_name',
      'last_name',
      'email',
      'status',
      'headline',
      'location',
      'locale',
      'timezone_code',
      'disable_promotion',
    )
    field_classes = None


class CustomUserChangeForm(UserChangeForm):
  class Meta(UserChangeForm.Meta):
    model = User
    fields = (
      'first_name',
      'last_name',
      'email',
      'image',
      'status',
      'headline',
      'location',
      'locale',
      'timezone_code',
      'disable_promotion',
    )
    field_classes = None
