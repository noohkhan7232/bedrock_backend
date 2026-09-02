from rest_framework import serializers

from api.base.serializers import (
  BaseModelSerializer,
  BaseSerializer,
)
from api.internal.v1.serializers.common import ReadOnlyTenantUserMinSerializer
from api.schema.decorators import extend_serializer_schema
from core.constants import TENANT_USER_ROLES
from core.models import (
  Tenant,
  TenantUser,
  TenantUserLink,
  User,
)
from core.services.tenant_email_policy import TenantEmailPolicy


class BaseTenantUserSerializer(BaseModelSerializer):
  tenant_id = serializers.IntegerField(write_only=True)
  user_id = serializers.IntegerField(write_only=True)
  role_uid = serializers.ChoiceField(
    choices=[role.uid for role in TENANT_USER_ROLES.as_list()],
    required=False,
    read_only=True,
    default=TENANT_USER_ROLES.MEMBER.uid,
  )

  class Meta(BaseModelSerializer.Meta):
    model = TenantUser
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'tenant',
      'user',
      'joined_at',
    )

  def validate(self, data):
    tenant = Tenant.objects.get(id=data['tenant_id'])
    user = User.objects.get(id=data['user_id'])

    TenantEmailPolicy.enforce_allowed(
      tenant=tenant, email=user.email)
    return data


@extend_serializer_schema(
  exclude_fields=('actor_tenant_user_id', 'target_tenant_user_id',)
)
class TenantUserRoleUpdateSerializer(BaseSerializer):
  actor_tenant_user_id = serializers.IntegerField(write_only=True)
  target_tenant_user_id = serializers.IntegerField(write_only=True)

  role_uid = serializers.ChoiceField(
    choices=[role.uid for role in TENANT_USER_ROLES.as_list()]
  )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['actor_tenant_user_id'] = self.get_tenant_user_id()
    data_copy['target_tenant_user_id'] = self.from_context(
      key='target_tenant_user_id',
    )
    return super().to_internal_value(data_copy)


class CurrentTenantUserUpdateSerializer(BaseTenantUserSerializer):
  class Meta(BaseTenantUserSerializer.Meta):
    exclude = None
    fields = ('title', 'description',)


@extend_serializer_schema(exclude_fields=('actor_tenant_user_id',))
class CurrentTenantUserDeleteSerializer(BaseSerializer):
  actor_tenant_user_id = serializers.IntegerField(write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['actor_tenant_user_id'] = self.get_tenant_user_id()
    return super().to_internal_value(data_copy)


@extend_serializer_schema(
  exclude_fields=('actor_tenant_user_id', 'target_tenant_user_id',)
)
class TenantUserDeleteSerializer(BaseSerializer):
  actor_tenant_user_id = serializers.IntegerField(write_only=True)
  target_tenant_user_id = serializers.IntegerField(write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['actor_tenant_user_id'] = self.get_tenant_user_id()
    data_copy['target_tenant_user_id'] = (
      self.from_context('target_tenant_user_id')
    )
    return super().to_internal_value(data_copy)


@extend_serializer_schema(exclude_fields=('tenant_user_id',))
class TenantUserLinkSerializer(BaseModelSerializer):
  name = serializers.CharField(min_length=1, max_length=1024)
  url = serializers.URLField(max_length=1024)

  tenant_user = ReadOnlyTenantUserMinSerializer(
    required=False,
    read_only=True,
  )
  tenant_user_id = serializers.IntegerField(write_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantUserLink


class MatchedTenantUserSerializer(ReadOnlyTenantUserMinSerializer):
  name_similarity = serializers.FloatField(read_only=True)

  class Meta(ReadOnlyTenantUserMinSerializer.Meta):
    fields = ReadOnlyTenantUserMinSerializer.Meta.fields + (
      'name_similarity',
    )
