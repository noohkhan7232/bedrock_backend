from django.core.mail import EmailMultiAlternatives

from core.models import EmailJob
from core.services.email.messages import TEMPLATE_MESSAGE_CLASSES


class MessageBuilder:
  @staticmethod
  def build(email_job_id: int) -> EmailMultiAlternatives:
    email_job = EmailJob.objects.get(id=email_job_id)
    email_type = email_job.email_type

    template_message_class = TEMPLATE_MESSAGE_CLASSES[email_type]
    template_message = template_message_class(email_job=email_job)

    return template_message.message
