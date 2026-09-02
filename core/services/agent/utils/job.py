import threading
from typing import Callable
from django.db.models import Q

from core.dtos.agent import EnqueueAgentJobDTO
from core.models import AgentJob


def create_agent_job(
  agent_chat_message_id: int,
  state: AgentJob.State = AgentJob.State.PENDING,
) -> AgentJob:
  return AgentJob.objects.create(
    agent_chat_message_id=agent_chat_message_id,
    state=state,
  )


def cancel_user_agent_jobs(user_id: int) -> None:
  query = (
    AgentJob.objects
      .filter(
        agent_chat_message__agent_chat__user__id=user_id,
        agent_chat_message__agent_chat__user__deleted_at__isnull=True,
      )
      .filter(Q(state=AgentJob.State.RUNNING) | Q(state=AgentJob.State.PENDING))
  )

  for job in query.all():
    job.cancel()
    job.save()


def dispatch_agent_job_thread(
  dto: EnqueueAgentJobDTO,
  agent_job_id: str,
  handler_key: str,
  target: Callable,
):
  t = threading.Thread(
    target=target,
    args=(dto.model_dump(), agent_job_id, handler_key,),
    daemon=True,
  )
  t.start()
