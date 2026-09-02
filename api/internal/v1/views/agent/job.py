from django.db import transaction

from rest_framework import status
from rest_framework.response import Response

from api.base.views import BaseInternalAPIView
from api.internal.v1.serializers.agent.job import AgentJobSerializer
from api.schema.decorators import extend_method_schema
from api.schema.internal.v1.decorators import extend_class_schema
from api.permissions import IsTenantMember
from core.models import AgentJob


@extend_class_schema
class TenantScopedAgentJobView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='agent_job',
    response=AgentJobSerializer,
  )
  def get(self, request, *args, **kwargs):
    agent_job_id = kwargs['agent_job_id']
    obj = AgentJob.objects.get(
      id=agent_job_id,
      agent_chat_message__agent_chat__user__id=request.user.id,
      agent_chat_message__agent_chat__user__deleted_at__isnull=True,
    )
    serializer = AgentJobSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_class_schema
class TenantScopedAgentJobCancelView(BaseInternalAPIView):
  permission_classes = (IsTenantMember,)

  @extend_method_schema(
    resource='agent_job_cancel',
    response=AgentJobSerializer,
  )
  @transaction.atomic
  def post(self, request, *args, **kwargs):
    agent_job_id = kwargs['agent_job_id']
    obj = AgentJob.objects.get(
      id=agent_job_id,
      agent_chat_message__agent_chat__user__id=request.user.id,
      agent_chat_message__agent_chat__user__deleted_at__isnull=True,
    )
    obj.cancel()
    obj.save()

    serializer = AgentJobSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)
