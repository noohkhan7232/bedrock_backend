from core.dtos.email import (
  EnqueueEmailJobDTO,
  PasswordResetTemplateVarsDTO,
)
from core.models import EmailJob
from core.services.email.jobs.enqueue import enqueue_email_jobs
from core.utils.email import ensure_valid_email, generate_dedupe_key


def send_password_reset_email(
  email: str,
  reset_code: str,
) -> EmailJob:
  template_vars = (
    PasswordResetTemplateVarsDTO(reset_code=reset_code).model_dump()
  )
  ensured_email = ensure_valid_email(email=email)
  email_type = EmailJob.EmailType.PASSWORD_RESET
  dedupe_key = generate_dedupe_key(
    email_type=email_type,
    to_email=ensured_email,
    tenant_id=None,
    options=template_vars,
  )

  dto: EnqueueEmailJobDTO = EnqueueEmailJobDTO(
    tenant_id=None,
    sender_user_id=None,
    email_type=email_type,
    to_email=ensured_email,
    template_vars=template_vars,
    dedupe_key=dedupe_key,
  )
  email_job = enqueue_email_jobs(dtos=[dto], send_now=True)

  return email_job
