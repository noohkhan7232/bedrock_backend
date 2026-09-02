from django.urls import path

from api.internal.v1.views.agent import (
  TenantScopedAgentChatListView,
  TenantScopedAgentChatMessageListView,
  TenantScopedAgentChatMessageView,
  TenantScopedAgentJobView,
  TenantScopedAgentJobCancelView,
)


app_name = 'internal_api_v1_agent'

tenant_url = 'tenants/<str:domain>/'

urlpatterns = [
  path(
    tenant_url + 'agents/assistant/chats/',
    TenantScopedAgentChatListView.as_view(),
    name='agent_chats',
  ),
  path(
    tenant_url + 'agents/assistant/chats/<uuid:agent_chat_id>/messages/',
    TenantScopedAgentChatMessageListView.as_view(),
    name='agent_chat_messages',
  ),
  path(
    tenant_url + (
      'agents/assistant/chats/<uuid:agent_chat_id>/'
      'messages/<int:agent_chat_message_id>/'
    ),
    TenantScopedAgentChatMessageView.as_view(),
    name='agent_chat_message',
  ),
  path(
    tenant_url + 'agents/assistant/jobs/<uuid:agent_job_id>/',
    TenantScopedAgentJobView.as_view(),
    name='agent_job',
  ),
  path(
    tenant_url + 'agents/assistant/jobs/<uuid:agent_job_id>/cancel/',
    TenantScopedAgentJobCancelView.as_view(),
    name='agent_job_cancel',
  ),
]
