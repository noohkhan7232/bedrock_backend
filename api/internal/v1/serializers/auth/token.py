from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField

from api.base.serializers import RequestContextMixin
from api.schema.decorators import extend_serializer_schema


@extend_serializer_schema(exclude_fields=('ip_address',))
class TokenPairSerializer(serializers.Serializer, RequestContextMixin):
  ip_address = serializers.CharField(
    max_length=64,
    required=False,
    allow_null=True,
    allow_blank=True,
    write_only=True,
    default='',
  )
  email = serializers.EmailField(
    max_length=255, required=True, write_only=True)
  password = PasswordField(
    required=False,
    allow_null=True,
    allow_blank=True,
    help_text='Required if sso_code is not given.',
  )
  sso_code = serializers.CharField(
    max_length=255,
    required=False,
    allow_null=True,
    allow_blank=True,
    write_only=True,
    help_text='Required if SSO user.',
  )

  access = serializers.CharField(
    read_only=True, help_text='Access token.')
  access_expires_in = serializers.IntegerField(
    read_only=True,
    help_text='Duration in seconds before the access token expires.',
  )
  refresh = serializers.CharField(
    read_only=True, help_text='Refresh token.')
  refresh_expires_in = serializers.IntegerField(
    read_only=True,
    help_text='Duration in seconds before the refresh token expires.',
  )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['ip_address'] = self.from_context(key='ip_address')
    return super().to_internal_value(data_copy)


class TokenRefreshSerializer(serializers.Serializer):
  refresh = serializers.CharField(required=True)
  access = serializers.CharField(read_only=True)
  access_expires_in = serializers.IntegerField(
    read_only=True,
    help_text='Duration in seconds before the access token expires.',
  )


class TokenRevokeSerializer(serializers.Serializer):
  refresh = serializers.CharField(required=True, write_only=True)
  message = serializers.CharField(read_only=True)
