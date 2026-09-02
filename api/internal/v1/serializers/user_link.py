from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from api.schema.decorators import extend_serializer_schema
from core.models import UserLink


@extend_serializer_schema(exclude_fields=('user_id',))
class UserLinkSerializer(BaseModelSerializer):
  user_id = serializers.IntegerField(write_only=True)
  name = serializers.CharField(min_length=1, max_length=1024)
  url = serializers.CharField(min_length=1, max_length=1024)

  class Meta(BaseModelSerializer.Meta):
    model = UserLink
    exclude = BaseModelSerializer.Meta.exclude + ('user',)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


class UserLinkUpdateSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = UserLink
    exclude = None
    fields = ('name', 'url', 'display_order',)
