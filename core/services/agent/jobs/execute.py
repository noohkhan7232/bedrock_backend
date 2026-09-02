from django.db import (
  close_old_connections,
  connection,
  transaction,
)

from core.dtos.agent import EnqueueAgentJobDTO
from core.exceptions import JobCancelledError
from core.models import AgentJob
from core.services.agent.handlers import resolve_handler
from core.services.agent.utils.callbacks import ThrottledCallbackHandler
from core.services.agent.utils.llm import create_llm
from core.services.agent.vector_store import get_retriever


def run_agent_job(
  dto_dict: dict,
  agent_job_id: str,
  handler_key: str,
) -> None:
  try:
    close_old_connections()
    dto = EnqueueAgentJobDTO(**dto_dict)
    handler = resolve_handler(handler_key=handler_key)

    with transaction.atomic():
      agent_job = (
        AgentJob.objects.select_for_update(of=('self',)).get(id=agent_job_id)
      )
      agent_job.start()
      agent_job.save(update_fields=['state', 'started_at'])

    def throttled_callback(**kwargs) -> bool:
      close_old_connections()
      disable_callback = False
      with transaction.atomic():
        is_cancelled = (
          AgentJob.objects
            .filter(
              id=agent_job_id,
              agent_chat_message__agent_chat__user_id=dto.user_id,
              agent_chat_message__agent_chat__user__deleted_at__isnull=True,
              state=AgentJob.State.CANCELLED,
            )
            .exists()
        )
        if is_cancelled:
          disable_callback = True
          raise JobCancelledError(f'AgentJob {agent_job_id} was cancelled.')

        agent_job = (
          AgentJob.objects.select_for_update(of=('self',)).get(id=agent_job_id)
        )
        agent_chat_message = agent_job.agent_chat_message
        agent_chat_message.content = kwargs.get('current_text', '')
        agent_chat_message.save(update_fields=['content'])

      return disable_callback

    throttled_callbacks = [
      ThrottledCallbackHandler(callback=throttled_callback, interval=1.0, concatenate_text=True),
    ]
    retriever = get_retriever(
      search_type='similarity_score_threshold',
      search_kwargs={ 'k': 5, 'score_threshold': 0.35 },
    )

    llm_instant = create_llm(llm_type='instant', streaming=True)
    llm_fast = create_llm(llm_type='fast', streaming=True)
    llm_standard = create_llm(llm_type='standard', streaming=True)

    content = handler(
      dto=dto,
      retriever=retriever,
      llm_instant=llm_instant,
      llm_fast=llm_fast,
      llm_standard=llm_standard,
      callbacks=throttled_callbacks,
    )

    with transaction.atomic():
      agent_job = (
        AgentJob.objects.select_for_update(of=('self',)).get(id=agent_job_id)
      )
      agent_chat_message = agent_job.agent_chat_message
      agent_chat_message.content = content
      # TODO: Truncate content??
      agent_chat_message.save(update_fields=['content'])
      agent_job.succeed()
      agent_job.save(update_fields=['state', 'finished_at'])
  except JobCancelledError as e:
    with transaction.atomic():
      agent_job = (
        AgentJob.objects.select_for_update(of=('self',)).get(id=agent_job_id)
      )
      agent_job.cancel(reason=str(e))
      agent_job.save(update_fields=['state', 'error'])
  except Exception as e:
    with transaction.atomic():
      agent_job = (
        AgentJob.objects.select_for_update(of=('self',)).get(id=agent_job_id)
      )
      agent_job.fail(error=str(e))
      agent_job.save(update_fields=['state', 'finished_at', 'error'])
  finally:
    close_old_connections()
    connection.close()
