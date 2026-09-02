from abc import ABC, abstractmethod
from typing import TypedDict

from django.core.mail import EmailMultiAlternatives

from core.models import EmailJob


class EmailPayload(TypedDict):
  message: EmailMultiAlternatives


class _EmailJobResult(TypedDict):
  state: EmailJob.State
  error: str | None = None
  reason: str | None = None


EmailJobResult = dict[int, _EmailJobResult]


class BaseEmailDriver(ABC):
  @abstractmethod
  def send_batch_emails(
    self,
    email_payloads: dict[int, EmailPayload],
  ) -> EmailJobResult:
    pass
