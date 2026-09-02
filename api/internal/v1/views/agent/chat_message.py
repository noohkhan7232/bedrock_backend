from django.db import transaction

from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.agent.chat_message import (
  AgentChatMessageMinSerializer,
  EnqueueAgentJobSerializer,
)
from api.internal.v1.serializers.agent.job import AgentJobSerializer
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import IsTenantMember
from core.dtos.agent import EnqueueAgentJobDTO
from core.services.agent.jobs.enqueue import enqueue_agent_job


@transaction.atomic
def _orchestrate_agent_response(
  request, agent_chat_id, agent_chat_message_id=None
):
  context = {
    'request': request,
    'agent_chat_id': agent_chat_id,
    'agent_chat_message_id': agent_chat_message_id,
  }
  serializer = EnqueueAgentJobSerializer(
    data=request.data,
    context=context,
  )
  serializer.is_valid(raise_exception=True)

  dto = EnqueueAgentJobDTO(**serializer.validated_data)
  agent_job, human_chat_message, ai_chat_message = (
    enqueue_agent_job(dto=dto, handler_key='assistant')
  )

  resp = dict()
  serializer = AgentJobSerializer(agent_job)
  resp['agent_job'] = serializer.data
  serializer = AgentChatMessageMinSerializer(human_chat_message)
  resp['human_chat_message'] = serializer.data
  serializer = AgentChatMessageMinSerializer(ai_chat_message)
  resp['ai_chat_message'] = serializer.data

  return resp


@extend_class_schema
class TenantScopedAgentChatMessageListView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='agent_chat_messages',
    request=EnqueueAgentJobSerializer,
    response=AgentJobSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    agent_chat_id = kwargs['agent_chat_id']

    resp = _orchestrate_agent_response(
      request=request,
      agent_chat_id=agent_chat_id,
      agent_chat_message_id=None,
    )

    return Response(resp, status=status.HTTP_201_CREATED)


@extend_class_schema
class TenantScopedAgentChatMessageView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='agent_chat_message',
    request=EnqueueAgentJobSerializer,
    response=AgentJobSerializer,
  )
  @transaction.atomic
  def put(self, request, *args, **kwargs):
    agent_chat_id = kwargs['agent_chat_id']
    agent_chat_message_id = kwargs['agent_chat_message_id']

    resp = _orchestrate_agent_response(
      request=request,
      agent_chat_id=agent_chat_id,
      agent_chat_message_id=agent_chat_message_id,
    )

    return Response(resp, status=status.HTTP_200_OK)
