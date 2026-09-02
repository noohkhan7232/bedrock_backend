from celery import shared_task
from django.db import close_old_connections, transaction

from core.models import EmailJob
from core.services.email.jobs.execute import send_email


@shared_task(
  bind=True,
  name='core.services.email.tasks.dispatch_email_jobs_task',
  acks_late=True,
  reject_on_worker_lost=True,
)
def dispatch_email_jobs_task(self, batch_size: int = 200) -> None:
  close_old_connections()
  """
  TODO:
  1. Get undone and scheduled jobs
  2. Call execute_email_job_task from here.
  Note: Celery tasks are created and executed in the celery worker created by this function.
  """


@shared_task(
  bind=True,
  name='core.services.email.tasks.execute_email_job_task',
  acks_late=True,
  reject_on_worker_lost=True,
)
def execute_email_job_task(self, email_job_id: int) -> None:
  close_old_connections()

  with transaction.atomic():
    (
      EmailJob.objects
        .filter(id=email_job_id)
        .update(last_task_id=self.request.id)
    )

  result = send_email(email_job_id=email_job_id)
  return result
