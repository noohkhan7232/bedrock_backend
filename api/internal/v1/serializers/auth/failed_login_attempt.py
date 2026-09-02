from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from core.models import FailedLoginAttempt


class FailedLoginAttemptSerializer(BaseModelSerializer):
  attempted_at = serializers.DateTimeField(
    required=False,
    read_only=True,
  )

  class Meta(BaseModelSerializer.Meta):
    model = FailedLoginAttempt
