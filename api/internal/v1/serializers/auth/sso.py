from django.conf import settings
from rest_framework import serializers

from api.base.serializers import BaseSerializer
from api.schema.decorators import extend_serializer_schema


@extend_serializer_schema(exclude_fields=('email_domain',))
class SsoAuthorizationUrlSerializer(BaseSerializer):
  email = serializers.CharField(
    max_length=255,
    required=True,
    write_only=True,
  )
  invitation_code = serializers.CharField(
    max_length=settings.TENANT_INVITATION_CODE_LENGTH,
    required=False,
    allow_blank=True,
    default='',
    write_only=True,
  )
  verification_code = serializers.CharField(
    max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH,
    required=False,
    allow_blank=True,
    default='',
    write_only=True,
  )

  authorization_url = serializers.CharField(
    max_length=1024,
    default='',
    read_only=True,
  )


class SsoEnablementStatusSerializer(BaseSerializer):
  email_domain = serializers.CharField(
    min_length=5,
    max_length=255,
    required=True,
    write_only=True,
  )
  sso_enabled = serializers.BooleanField(read_only=True)
  message = serializers.CharField(read_only=True)
