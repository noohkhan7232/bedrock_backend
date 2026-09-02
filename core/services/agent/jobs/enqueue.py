from django.db import transaction, IntegrityError

from core.dtos.agent import EnqueueAgentJobDTO
from core.models import AgentChat, AgentChatMessage, AgentJob, TenantUser, User
from core.services.agent.utils.chat_message import (
  create_ai_chat_message,
  create_human_chat_message,
  update_human_chat_message,
)
from core.services.agent.utils.job import (
  create_agent_job,
  cancel_user_agent_jobs,
)
from core.services.agent.tasks import dispatch_agent_job_task
from core.services.agent.utils.pii_mask import pii_masker
from core.services.agent.utils.sanitize import sanitize_user_query


@transaction.atomic
def enqueue_agent_job(
  dto: EnqueueAgentJobDTO,
  handler_key: str,
) -> tuple[AgentJob, AgentChatMessage, AgentChatMessage]:
  query = AgentChat.objects.filter(id=dto.agent_chat_id, user_id=dto.user_id)

  if dto.tenant_id is not None:
    if not TenantUser.available.filter(
      tenant_id=dto.tenant_id,
      user_id=dto.user_id,
    ).exists():
      raise ValueError('Tenant user not found.')
    query = query.filter(tenant_id=dto.tenant_id)
  elif not User.objects.filter(id=dto.user_id).exists():
    raise ValueError('User not found')

  if not query.exists():
    raise ValueError('Agent chat not found.')
  try:
    dto.content = sanitize_user_query(dto.content)
    dto.content = pii_masker.mask(text=dto.content)

    cancel_user_agent_jobs(user_id=dto.user_id)

    rewind_chat = dto.agent_chat_message_id is not None
    if rewind_chat:
      human_chat_message = update_human_chat_message(
        user_id=dto.user_id,
        content=dto.content,
        agent_chat_id=dto.agent_chat_id,
        agent_chat_message_id=dto.agent_chat_message_id,
      )
    else:
      human_chat_message = create_human_chat_message(
        agent_chat_id=dto.agent_chat_id,
        content=dto.content,
      )

    ai_chat_message = create_ai_chat_message(
      agent_chat_id=dto.agent_chat_id,
      content='',
    )
    agent_job = create_agent_job(
      agent_chat_message_id=ai_chat_message.id,
      state=AgentJob.State.PENDING,
    )

    def _dispatch():
      dispatch_agent_job_task.apply_async(
        args=[dto.model_dump(), str(agent_job.id), handler_key],
        queue='llm',
      )
    transaction.on_commit(_dispatch)

    return agent_job, human_chat_message, ai_chat_message
  except IntegrityError as e:
    raise ValueError('Failed to enqueue agent job.') from e
