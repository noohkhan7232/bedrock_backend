from django.db import (
  close_old_connections,
  connection,
  transaction,
)

from core.exceptions import JobCancelledError
from core.models import EmailJob
from core.services.email.drivers import get_email_driver
from core.services.email.drivers.base import (
  EmailJobResult,
  EmailPayload,
)

from core.services.email.messages.builder import MessageBuilder


def send_email(email_job_id: int) -> None:
  try:
    close_old_connections()

    with transaction.atomic():
      email_job = (
        EmailJob.objects.select_for_update(of=('self',)).get(id=email_job_id)
      )
      email_job.start()
      email_job.save(update_fields=['state', 'started_at'])

    email_payloads: dict[int, EmailPayload] = {
      email_job_id: {
        'message': MessageBuilder.build(email_job_id=email_job_id)
      },
    }

    email_driver = get_email_driver()
    email_job_results: EmailJobResult = (
      email_driver.send_batch_emails(email_payloads=email_payloads)
    )

    with transaction.atomic():
      email_job = (
        EmailJob.objects.select_for_update(of=('self',)).get(id=email_job_id)
      )
      if email_job_id in email_job_results:
        email_job.succeed()
        email_job.save(update_fields=['state', 'finished_at'])
      else:
        email_job.fail(error='Corresponding email job result was not found.')
        email_job.save(update_fields=['state', 'finished_at', 'error'])
  except JobCancelledError as e:
    with transaction.atomic():
      email_job = (
        EmailJob.objects.select_for_update(of=('self',)).get(id=email_job_id)
      )
      email_job.cancel(reason=str(e))
      email_job.save(update_fields=['state', 'error'])
  except Exception as e:
    with transaction.atomic():
      email_job = (
        EmailJob.objects.select_for_update(of=('self',)).get(id=email_job_id)
      )
      email_job.fail(error=str(e))
      email_job.save(update_fields=['state', 'finished_at', 'error'])
  finally:
    close_old_connections()
    connection.close()
