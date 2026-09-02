from django.conf import settings
from rest_framework import serializers

from api.base.serializers import BaseModelSerializer, BaseSerializer
from api.internal.v1.serializers.common import (
  ReadOnlyTenantSerializer,
  ReadOnlyTenantUserMinSerializer,
)
from api.internal.v1.serializers.tenant import (
  ReadOnlyTenantDetailSerializer,
)
from api.schema.decorators import extend_serializer_schema
from core.models import TenantInvitationCode


@extend_serializer_schema(exclude_fields=('user_id',))
class CurrentUserTenantInvitationCodeSerializer(BaseSerializer):
  user_id = serializers.IntegerField(write_only=True)
  invitation_code = serializers.CharField(
    write_only=True,
    help_text=(
      'The unique code provided in the tenant-joining link '
      'sent by `tenant_invitation_codes` API.'
    ),
  )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


class TenantInvitationCodeDetailSerializer(BaseModelSerializer):
  tenant = ReadOnlyTenantDetailSerializer(read_only=True)
  invited_by = ReadOnlyTenantUserMinSerializer(read_only=True, allow_null=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantInvitationCode


@extend_serializer_schema(exclude_fields=('tenant_id',))
class TenantInvitationCodeSerializer(BaseModelSerializer):
  tenant_id = serializers.IntegerField(required=True, write_only=True)
  tenant = ReadOnlyTenantSerializer(read_only=True)

  invitation_code = serializers.CharField(
    read_only=True,
    help_text=(
      'The unique code provided in the tenant-joining link '
      'sent by `tenant_invitation_codes` API.'
    ),
  )
  invited_by = ReadOnlyTenantUserMinSerializer(read_only=True, allow_null=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantInvitationCode
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'valid_until',
    )


@extend_serializer_schema(exclude_fields=('tenant_id', 'tenant_user_id',))
class TenantInvitationCodeListSerializer(BaseSerializer):
  tenant_id = serializers.IntegerField(write_only=True)
  tenant_user_id = serializers.IntegerField(write_only=True)
  emails = serializers.ListField(
    child=serializers.EmailField(min_length=6),
    min_length=1,
    required=True,
    write_only=True,
  )

  tenant_invitation_codes = TenantInvitationCodeSerializer(
    many=True,
    read_only=True,
    help_text=(
      'List of the unique codes provided in the tenant-joining link '
      'sent by `tenant_invitation_codes` API.'
    ),
  )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['tenant_id'] = self.get_tenant_id()
    data_copy['tenant_user_id'] = self.get_tenant_user_id()
    return super().to_internal_value(data_copy)


class TenantInvitationCodeEmailSerializer(BaseSerializer):
  invitation_code = serializers.CharField(
    min_length=settings.TENANT_INVITATION_CODE_LENGTH,
    max_length=settings.TENANT_INVITATION_CODE_LENGTH,
    write_only=True,
    help_text=(
      'The unique code provided in the tenant-joining link '
      'sent by `tenant_invitation_codes` API.'
    ),
  )
  email = serializers.EmailField(read_only=True)


class TenantInvitationCodeTenantSerializer(BaseSerializer):
  invitation_code = serializers.CharField(
    min_length=settings.TENANT_INVITATION_CODE_LENGTH,
    max_length=settings.TENANT_INVITATION_CODE_LENGTH,
    write_only=True,
    help_text=(
      'The unique code provided in the tenant-joining link '
      'sent by `tenant_invitation_codes` API.'
    ),
  )
