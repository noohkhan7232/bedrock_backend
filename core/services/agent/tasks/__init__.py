from celery import shared_task
from django.db import close_old_connections, transaction

from core.models import AgentJob
from core.services.agent.jobs.execute import run_agent_job


@shared_task(
  bind=True,
  name='core.services.agent.tasks.dispatch_agent_job_task',
  acks_late=True,
  reject_on_worker_lost=True,
)
def dispatch_agent_job_task(
  self,
  dto_dict: dict,
  agent_job_id: str,
  handler_key: str,
):
  close_old_connections()

  with transaction.atomic():
    AgentJob.objects.filter(id=agent_job_id).update(last_task_id=self.request.id)

  result = run_agent_job(
    dto_dict=dto_dict, agent_job_id=agent_job_id, handler_key=handler_key)

  return result
