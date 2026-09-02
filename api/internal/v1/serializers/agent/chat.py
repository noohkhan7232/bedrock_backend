from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from api.internal.v1.serializers.common import (
  ReadOnlyTenantMinSerializer,
  ReadOnlyUserMinSerializer,
)
from core.models import AgentChat


class BaseAgentChatSerializer(BaseModelSerializer):
  tenant_id = serializers.IntegerField(
    required=False,
    allow_null=True,
    write_only=True,
    min_value=1,
    default=None,
  )
  user_id = serializers.IntegerField(write_only=True, min_value=1)

  tenant = ReadOnlyTenantMinSerializer(allow_null=True, read_only=True)
  user = ReadOnlyUserMinSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = AgentChat
    exclude = None
    fields = (
      'id',
      'user', 'user_id',
      'tenant', 'tenant_id',
      'agent_type',
      'created_at',
    )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['agent_type'] = 'assistant'
    data_copy['tenant_id'] = self.get_tenant_id(raise_exception=False)
    data_copy['user_id'] = self.get_user_id(raise_exception=True)
    return super().to_internal_value(data_copy)


class AgentChatSerializer(BaseAgentChatSerializer):
  class Meta(BaseAgentChatSerializer.Meta):
    pass


class AgentChatMinSerializer(BaseAgentChatSerializer):
  class Meta(BaseAgentChatSerializer.Meta):
    fields = (
      'id',
      'agent_type',
    )
