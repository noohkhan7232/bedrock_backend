from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.base.serializers import BaseModelSerializer
from api.internal.v1.serializers.common import (
  ReadOnlyTenantRefSerializer,
)
from api.schema.decorators import extend_serializer_schema
from core.models import TenantTag
from core.utils.text import normalize


class BaseTenantTagSerializer(BaseModelSerializer):
  tenant_id = serializers.IntegerField(write_only=True)
  name = serializers.CharField(min_length=1, max_length=255)
  tenant = ReadOnlyTenantRefSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = TenantTag

  def validate(self, data):
    data['name'] = normalize(data['name'])

    query = TenantTag.objects.filter(
      tenant_id=data['tenant_id'], name__iexact=data['name'])
    if query.exists():
      raise ValidationError('Tag already exists.')

    return data


@extend_serializer_schema(exclude_fields=('tenant_id',))
class TenantTagSerializer(BaseTenantTagSerializer):
  class Meta(BaseTenantTagSerializer.Meta):
    pass


class TenantTagMinSerializer(BaseTenantTagSerializer):
  tenant = ReadOnlyTenantRefSerializer(read_only=True)

  class Meta(BaseTenantTagSerializer.Meta):
    exclude = None
    fields = (
      'id',
      'tenant',
      'name',
    )
