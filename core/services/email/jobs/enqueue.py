from collections.abc import Sequence
from django.db import transaction, IntegrityError

from core.constants import CONSTANTS
from core.dtos.email import EnqueueEmailJobDTO
from core.models import EmailJob, Tenant
from core.services.email.tasks import execute_email_job_task


def enqueue_email_jobs(
  dtos: Sequence[EnqueueEmailJobDTO],
  send_now: bool = False,
) -> list[EmailJob]:
  if not dtos:
    return []

  tenant_ids = set([dto.tenant_id for dto in dtos if dto.tenant_id is not None])
  if (
    tenant_ids
    and Tenant.objects.filter(id__in=tenant_ids).count() != len(tenant_ids)
  ):
    raise ValueError('Tenant not found')

  email_jobs: list[EmailJob] = []

  for dto in dtos:
    if dto.email_type not in EmailJob.EmailType.values:
      raise ValueError(f'Invalid email_type: {dto.email_type}')

    try:
      with transaction.atomic():
        email_job = EmailJob.objects.create(**dto.model_dump())
    except IntegrityError as e:
      email_job = (
        EmailJob.objects
          .filter(
            dedupe_key=dto.dedupe_key,
            state__in=[EmailJob.State.PENDING, EmailJob.State.RUNNING],
          )
          .first()
      )
      if email_job is None:
        raise e

    email_jobs.append(email_job)

  if send_now:
    def _dispatch():
      if len(email_jobs) > CONSTANTS.EMAIL_BATCH_SIZE:
        raise NotImplementedError(
          'Sending emails per batch is not supported yet.'
        )
      else:
        for email_job in email_jobs:
          execute_email_job_task.apply_async(
            args=[email_job.id],
            queue='default',
          )

    transaction.on_commit(_dispatch)

  return email_jobs
