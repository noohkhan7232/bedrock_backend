from django.db import transaction, IntegrityError

from core.dtos.agent import CreateAgentChatDTO
from core.models import AgentChat, TenantUser, User


def create_agent_chat(dto: CreateAgentChatDTO):
  if dto.tenant_id is not None:
    if not TenantUser.available.filter(
      tenant_id=dto.tenant_id,
      user_id=dto.user_id,
    ).exists():
      raise ValueError('Tenant user not found.')
  elif not User.objects.filter(id=dto.user_id).exists():
    raise ValueError('User not found.')

  try:
    with transaction.atomic():
      payload = dto.model_dump()
      obj = AgentChat.objects.create(**payload)
      return obj
  except IntegrityError as e:
    raise ValueError('Failed to create AgentChat') from e
