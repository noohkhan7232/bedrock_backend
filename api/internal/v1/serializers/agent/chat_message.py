from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from api.internal.v1.serializers.agent.chat import (
  AgentChatSerializer,
  AgentChatMinSerializer,
)
from core.models import AgentChatMessage


class BaseAgentChatMessageSerializer(BaseModelSerializer):
  agent_chat_id = serializers.UUIDField(write_only=True)
  agent_chat = AgentChatSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = AgentChatMessage
    exclude = None
    fields = (
      'id',
      'agent_chat', 'agent_chat_id',
      'sender',
      'content',
    )


class AgentChatMessageSerializer(BaseAgentChatMessageSerializer):
  class Meta(BaseAgentChatMessageSerializer.Meta):
    pass


class AgentChatMessageMinSerializer(BaseAgentChatMessageSerializer):
  agent_chat = AgentChatMinSerializer(read_only=True)

  class Meta(BaseAgentChatMessageSerializer.Meta):
    pass


class EnqueueAgentJobSerializer(BaseAgentChatMessageSerializer):
  tenant_id = serializers.IntegerField(
    required=False, allow_null=True, write_only=True, default=None)
  user_id = serializers.IntegerField(write_only=True)
  agent_chat_message_id = serializers.IntegerField(
    required=False, allow_null=True, write_only=True, default=None)

  class Meta(BaseAgentChatMessageSerializer.Meta):
    fields = (
      'id',
      'agent_chat_id',
      'agent_chat_message_id',
      'content',
      'tenant_id',
      'user_id',
    )

  def to_internal_value(self, data):
    data_copy = data.copy()
    data_copy['agent_chat_id'] = self.from_context(
      key='agent_chat_id', raise_exception=True)
    data_copy['tenant_id'] = self.get_tenant_id(raise_exception=False)
    data_copy['user_id'] = self.get_user_id(raise_exception=True)
    data_copy['agent_chat_message_id'] = self.from_context(
      key='agent_chat_message_id', raise_exception=False, default_value=None)

    return super().to_internal_value(data_copy)
