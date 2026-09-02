from django.db import transaction

from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.agent.chat import AgentChatSerializer
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import IsTenantMember
from core.dtos.agent import CreateAgentChatDTO
from core.services.agent.utils.chat import create_agent_chat


@extend_class_schema
class TenantScopedAgentChatListView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='agent_chats',
    request=AgentChatSerializer,
    response=AgentChatSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    serializer = AgentChatSerializer(
      data=request.data,
      context={ 'request': request },
    )
    serializer.is_valid(raise_exception=True)

    dto = CreateAgentChatDTO(**serializer.validated_data)
    obj = create_agent_chat(dto=dto)

    serializer = AgentChatSerializer(obj)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
