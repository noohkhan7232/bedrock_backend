from rest_framework import serializers

from api.base.serializers import BaseModelSerializer
from api.internal.v1.serializers.agent.chat_message import (
  AgentChatMessageMinSerializer,
)
from core.models import AgentJob


class BaseAgentJobSerializer(BaseModelSerializer):
  agent_chat_message_id = serializers.IntegerField(
    write_only=True,
    min_value=1,
  )
  agent_chat_message = AgentChatMessageMinSerializer(read_only=True)

  class Meta(BaseModelSerializer.Meta):
    model = AgentJob
    exclude = None
    fields = (
      'id',
      'agent_chat_message', 'agent_chat_message_id',
      'state',
      'error',
      'started_at',
      'finished_at',
    )


class AgentJobSerializer(BaseAgentJobSerializer):
  class Meta(BaseAgentJobSerializer.Meta):
    pass
