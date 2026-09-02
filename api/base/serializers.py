from rest_framework import serializers

from core.exceptions import PayloadTooLargeError


class RequestContextMixin:
  def _get_request(self, raise_exception=True):
    request = self.context.get('request')
    if not request and raise_exception:
      raise serializers.ValidationError(
        'Serializer requires a request in context.'
      )
    return request

  def from_context(self, key, raise_exception=True, default_value=None):
    if key not in self.context:
      if raise_exception:
        raise serializers.ValidationError(
          f'Serializer requires {key} in context.'
        )
      return default_value
    return self.context.get(key)

  def get_tenant_user(self, raise_exception=True):
    request = self._get_request(raise_exception=raise_exception)
    if not request:
      return None

    return getattr(request, 'tenant_user', None)

  def get_user_id(self, raise_exception=True):
    request = self._get_request(raise_exception=raise_exception)
    if not request:
      return None

    user = getattr(request, 'user', None)
    if not user:
      tenant_user = self.get_tenant_user(raise_exception=raise_exception)
      user = getattr(tenant_user, 'user', None)

    if user and user.is_authenticated:
      return user.id

    if raise_exception:
      raise serializers.ValidationError(
        'Serializer requires a request.user or request.tenant_user in context.'
      )
    return None

  def get_tenant_id(self, raise_exception=True):
    request = self._get_request(raise_exception=raise_exception)
    if not request:
      return None

    tenant = getattr(request, 'tenant', None)
    if not tenant:
      tenant_user = self.get_tenant_user(raise_exception=raise_exception)
      tenant = getattr(tenant_user, 'tenant', None)

    if tenant:
      return tenant.id

    if raise_exception:
      raise serializers.ValidationError(
        'Serializer requires a request.tenant or request.tenant_user in context.'
      )
    return None

  def get_tenant_user_id(self, raise_exception=True):
    tenant_user = self.get_tenant_user(raise_exception=raise_exception)
    if tenant_user:
      return tenant_user.id

    if raise_exception:
      raise serializers.ValidationError(
        'Serializer requires a request.tenant_user in context.'
      )


class DefaultListSerializer(serializers.ListSerializer):
  MAX_ITEMS = 20

  def validate(self, data):
    if len(data) > self.MAX_ITEMS:
      raise PayloadTooLargeError(
        f'Request list size must be <= {self.MAX_ITEMS}.'
      )
    return data


class BaseSerializer(serializers.Serializer, RequestContextMixin):
  class Meta:
    list_serializer_class = DefaultListSerializer


class BaseModelSerializer(serializers.ModelSerializer, RequestContextMixin):
  def get_fields(self):
    fields = super().get_fields()
    fields.pop('deleted_at', None)
    return fields

  class Meta:
    exclude = ('created_at', 'updated_at',)
    read_only_fields = ('id',)
    list_serializer_class = DefaultListSerializer
