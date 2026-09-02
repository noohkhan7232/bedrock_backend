from rest_framework import serializers

from api.base.serializers import BaseModelSerializer, BaseSerializer
from api.schema.decorators import (
  extend_method_field_schema,
  extend_serializer_schema,
)
from core.constants import PLANS
from core.models import (
  Tenant,
  TenantBlacklistedEmailDomain,
  TenantEmailPolicyConfig,
  TenantWhitelistedEmail,
  TenantWhitelistedEmailDomain,
)
from core.services.subscription import (
  get_tenant_plan_uid,
  get_tenant_subscription,
)
from core.services.tenant import (
  get_tenant_admins,
  get_tenant_user_count as get_tenant_user_count_impl,
)
from core.services.tenant_email_policy import (
  get_tenant_email_policy_config,
  get_tenant_blacklisted_email_domains,
  get_tenant_whitelisted_email_domains,
  get_tenant_whitelisted_emails,
)
from api.internal.v1.serializers.common import (
  ReadOnlyTenantRefSerializer,
  ReadOnlyTenantUserMinSerializer,
)


class ReadOnlyTenantEmailPolicyConfigMinSerializer(
  BaseModelSerializer,
):
  tenant = ReadOnlyTenantRefSerializer()

  class Meta(BaseModelSerializer.Meta):
    model = TenantEmailPolicyConfig
    exclude = None
    fields = (
      'id',
      'tenant',
      'default_policy_uid',
      'email_whitelist_overrides_blacklist',
    )


class ReadOnlyTenantBlacklistedEmailDomainMinSerializer(
  BaseModelSerializer,
):
  tenant = ReadOnlyTenantRefSerializer()

  class Meta(BaseModelSerializer.Meta):
    model = TenantBlacklistedEmailDomain
    exclude = None
    fields = (
      'id',
      'tenant',
      'domain',
      'include_subdomains',
    )


class ReadOnlyTenantWhitelistedEmailDomainMinSerializer(
  BaseModelSerializer,
):
  tenant = ReadOnlyTenantRefSerializer()

  class Meta(BaseModelSerializer.Meta):
    model = TenantWhitelistedEmailDomain
    exclude = None
    fields = (
      'id',
      'tenant',
      'domain',
      'include_subdomains',
    )


class ReadOnlyTenantWhitelistedEmailMinSerializer(
  BaseModelSerializer,
):
  tenant = ReadOnlyTenantRefSerializer()

  class Meta(BaseModelSerializer.Meta):
    model = TenantWhitelistedEmail
    exclude = None
    fields = (
      'id',
      'tenant',
      'email',
    )


class ReadOnlyTenantDetailSerializer(BaseModelSerializer):
  tenant_user_count = serializers.SerializerMethodField()
  admins = serializers.SerializerMethodField()

  plan_uid = serializers.SerializerMethodField()
  subscribed_at = serializers.SerializerMethodField()
  expires_at = serializers.SerializerMethodField()

  email_policy_config = serializers.SerializerMethodField()
  blacklisted_email_domains = serializers.SerializerMethodField()
  whitelisted_email_domains = serializers.SerializerMethodField()
  whitelisted_emails = serializers.SerializerMethodField()

  class Meta(BaseModelSerializer.Meta):
    model = Tenant
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'account_id',
      'domain',
    )
    exclude = BaseModelSerializer.Meta.exclude + ('image',)

  @extend_method_field_schema(int)
  def get_tenant_user_count(self, obj):
    return get_tenant_user_count_impl(tenant_id=obj.id)

  @extend_method_field_schema(ReadOnlyTenantUserMinSerializer, many=True)
  def get_admins(self, obj):
    admins = get_tenant_admins(tenant_id=obj.id, max_length=3)
    serializer = ReadOnlyTenantUserMinSerializer(admins, many=True)
    return serializer.data

  @extend_method_field_schema(int)
  def get_plan_uid(self, obj):
    return get_tenant_plan_uid(tenant_id=obj.id)

  @extend_method_field_schema(str)
  def get_subscribed_at(self, obj):
    subscription = get_tenant_subscription(tenant_id=obj.id)
    return None if subscription is None else subscription.subscribed_at

  @extend_method_field_schema(str)
  def get_expires_at(self, obj):
    subscription = get_tenant_subscription(tenant_id=obj.id)
    return None if subscription is None else subscription.expires_at

  @extend_method_field_schema(ReadOnlyTenantEmailPolicyConfigMinSerializer)
  def get_email_policy_config(self, obj):
    config = get_tenant_email_policy_config(tenant_id=obj.id)
    serializer = ReadOnlyTenantEmailPolicyConfigMinSerializer(
      config,
    )
    return serializer.data

  @extend_method_field_schema(
    ReadOnlyTenantBlacklistedEmailDomainMinSerializer,
    many=True,
  )
  def get_blacklisted_email_domains(self, obj):
    domains = get_tenant_blacklisted_email_domains(tenant_id=obj.id)
    serializer = ReadOnlyTenantBlacklistedEmailDomainMinSerializer(
      domains,
      many=True,
    )
    return serializer.data

  @extend_method_field_schema(
    ReadOnlyTenantWhitelistedEmailDomainMinSerializer,
    many=True,
  )
  def get_whitelisted_email_domains(self, obj):
    domains = get_tenant_whitelisted_email_domains(tenant_id=obj.id)
    serializer = ReadOnlyTenantWhitelistedEmailDomainMinSerializer(
      domains,
      many=True,
    )
    return serializer.data

  @extend_method_field_schema(
    ReadOnlyTenantWhitelistedEmailMinSerializer,
    many=True,
  )
  def get_whitelisted_emails(self, obj):
    emails = get_tenant_whitelisted_emails(tenant_id=obj.id)
    serializer = ReadOnlyTenantWhitelistedEmailMinSerializer(
      emails,
      many=True,
    )
    return serializer.data


class TenantUpdateSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = Tenant
    exclude = None
    fields = ('name', 'description',)


@extend_serializer_schema(exclude_fields=('tenant_id', 'user_id',))
class TenantDeleteSerializer(BaseSerializer):
  tenant_id = serializers.IntegerField(write_only=True)
  user_id = serializers.IntegerField(write_only=True)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['tenant_id'] = self.get_tenant_id()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


@extend_serializer_schema(exclude_fields=('user_id',))
class NewTenantSerializer(BaseSerializer):
  name = serializers.CharField(
    min_length=1, max_length=255, write_only=True)
  description = serializers.CharField(
    min_length=0,
    max_length=1024,
    write_only=True,
    default='',
  )

  user_id = serializers.IntegerField(write_only=True)
  plan_uid = serializers.ChoiceField(
    choices=[plan.uid for plan in PLANS.as_list()],
    required=False,
    write_only=True,
    default=PLANS.FREE.uid,
  )
  months = serializers.IntegerField(
    min_value=0, max_value=60, required=False, write_only=True, default=12)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)
