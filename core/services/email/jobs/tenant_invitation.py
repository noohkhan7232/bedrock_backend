from core.dtos.email import (
  EnqueueEmailJobDTO,
  TenantInviteTemplateVarsDTO,
)
from core.models import EmailJob
from core.services.email.jobs.enqueue import enqueue_email_jobs
from core.utils.email import ensure_valid_email, generate_dedupe_key


def send_invitation_email(
  tenant_id: int,
  user_id: int,
  email: str,
  invitation_code: str,
) -> EmailJob:
  template_vars = TenantInviteTemplateVarsDTO(
    invitation_code=invitation_code,
  ).model_dump()
  ensured_email = ensure_valid_email(email=email)
  email_type = EmailJob.EmailType.TENANT_INVITE
  dedupe_key = generate_dedupe_key(
    email_type=email_type,
    to_email=ensured_email,
    tenant_id=tenant_id,
    options=template_vars,
  )

  dto = EnqueueEmailJobDTO(
    tenant_id=tenant_id,
    sender_user_id=user_id,
    email_type=email_type,
    to_email=ensured_email,
    template_vars=template_vars,
    dedupe_key=dedupe_key,
  )
  email_job = enqueue_email_jobs(dtos=[dto], send_now=True)

  return email_job

