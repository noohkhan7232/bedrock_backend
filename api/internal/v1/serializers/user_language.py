from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from api.schema.decorators import extend_serializer_schema
from core.constants.language import (
  APP_LANGUAGE_CODE_CHOICES,
  LANGUAGE_PROFICIENCIES,
)
from core.models import UserLanguage


@extend_serializer_schema(exclude_fields=('user_id',))
class UserLanguageSerializer(BaseModelSerializer):
  user_id = serializers.IntegerField(write_only=True)
  language_code = serializers.ChoiceField(
    choices=APP_LANGUAGE_CODE_CHOICES,
    required=True,
  )
  proficiency_uid = serializers.ChoiceField(
    required=True, choices=LANGUAGE_PROFICIENCIES.get_uid_list())
  display_order = serializers.IntegerField(required=False, default=0)

  class Meta(BaseModelSerializer.Meta):
    model = UserLanguage
    exclude = BaseModelSerializer.Meta.exclude + ('user',)

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['user_id'] = self.get_user_id()
    return super().to_internal_value(data_copy)


class UserLanguageUpdateSerializer(BaseModelSerializer):
  class Meta(BaseModelSerializer.Meta):
    model = UserLanguage
    exclude = None
    fields = ('language_code', 'proficiency_uid', 'display_order',)
