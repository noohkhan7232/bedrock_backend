from core.dtos.email import (
  EnqueueEmailJobDTO,
  SignupWelcomeTemplateVarsDTO,
)
from core.models import EmailJob
from core.services.email.jobs.enqueue import enqueue_email_jobs
from core.utils.email import ensure_valid_email, generate_dedupe_key


def send_signup_welcome_email(
  email: str,
  tenant_id: int | None,
) -> EmailJob:
  template_vars = SignupWelcomeTemplateVarsDTO().model_dump()
  ensured_email = ensure_valid_email(email=email)
  email_type = EmailJob.EmailType.SIGNUP_WELCOME
  dedupe_key = generate_dedupe_key(
    email_type=email_type,
    to_email=ensured_email,
    tenant_id=tenant_id,
    options=template_vars,
  )

  dto: EnqueueEmailJobDTO = EnqueueEmailJobDTO(
    tenant_id=tenant_id,
    sender_user_id=None,
    email_type=email_type,
    to_email=ensured_email,
    template_vars=template_vars,
    dedupe_key=dedupe_key,
  )
  email_job = enqueue_email_jobs(dtos=[dto], send_now=True)

  return email_job
