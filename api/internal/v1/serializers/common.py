from api.base.serializers import BaseModelSerializer
from core.models import User, Tenant, TenantUser


class ReadOnlyUserSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = User
    exclude = None
    fields = (
      'id',
      'first_name',
      'last_name',
      'email',
      'image',
      'headline',
      'location',
      'locale',
      'timezone_code',
    )


class ReadOnlyUserMinSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = User
    exclude = None
    fields = (
      'id',
      'first_name',
      'last_name',
      'email',
      'image',
      'headline',
    )


class ReadOnlyTenantSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = Tenant
    exclude = None
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'domain',
    )
    fields = (
      'id',
      'name',
      'domain',
      'description',
    )


class ReadOnlyTenantMinSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = Tenant
    exclude = None
    read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
      'domain',
    )
    fields = (
      'id',
      'name',
      'domain',
    )


class ReadOnlyTenantRefSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = Tenant
    exclude = None
    fields = (
      'id',
    )


class ReadOnlyTenantUserMinSerializer(BaseModelSerializer):
  tenant = ReadOnlyTenantRefSerializer(read_only=True)
  user = ReadOnlyUserMinSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantUser
    exclude = None
    fields = (
      'id',
      'tenant',
      'user',
      'title',
      'role_uid',
    )


class ReadOnlyTenantUserSerializer(BaseModelSerializer):
  tenant = ReadOnlyTenantRefSerializer(read_only=True)
  user = ReadOnlyUserSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantUser
    exclude = None
    fields = (
      'id',
      'tenant',
      'user',
      'title',
      'role_uid',
      'description',
      'disable_email_notification',
    )
