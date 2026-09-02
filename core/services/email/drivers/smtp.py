import logging
import smtplib

from django.conf import settings
from django.core.mail import get_connection

from core.exceptions import EmailServiceError
from core.models import EmailJob
from core.services.email.drivers.base import (
  BaseEmailDriver,
  EmailPayload,
  EmailJobResult,
)

logger = logging.getLogger(__name__)


class SmtpDriver(BaseEmailDriver):
  ATTEMPTS_MAX = 2

  def send_batch_emails(
    self,
    email_payloads: dict[int, EmailPayload],
    batch_size: int = 100,
  ) -> EmailJobResult:
    if not email_payloads:
      return {}

    if len(email_payloads) > batch_size:
      raise ValueError('Too many email_payloads is given.')

    email_job_results: EmailJobResult = {}
    pending_email_payloads = dict(email_payloads)

    for attempt in range(self.ATTEMPTS_MAX):
      if not pending_email_payloads:
        break

      pending_email_payloads = self._send_attempt(
        pending_email_payloads=pending_email_payloads,
        email_job_results=email_job_results,
        attempt=attempt,
      )

    return email_job_results

  def _send_attempt(
    self,
    pending_email_payloads: dict[int, EmailPayload],
    email_job_results: EmailJobResult,
    attempt: int,
  ) -> dict[int, EmailPayload]:
    connection = self._get_connection()
    items = list(pending_email_payloads.items())
    retry_email_payloads: dict[int, EmailPayload] = {}
    is_last_attempt = attempt >= self.ATTEMPTS_MAX - 1

    try:
      connection.open()

      for index, (email_job_id, payload) in enumerate(items):
        try:
          sent = self._send_one_email(
            connection=connection,
            email_job_id=email_job_id,
            payload=payload,
          )
          if sent:
            email_job_results[email_job_id] = {
              'state': EmailJob.State.DONE,
              'error': '',
            }
          elif is_last_attempt:
            self._mark_failed(
              email_job_results=email_job_results,
              email_job_id=email_job_id,
              error='SMTP send returned sent_count != 1',
            )
          else:
            retry_email_payloads[email_job_id] = payload

        except smtplib.SMTPServerDisconnected as e:
          logger.exception(e)

          remaining_items = items[index:]
          if is_last_attempt:
            for retry_email_job_id, _ in remaining_items:
              self._mark_failed(
                email_job_results=email_job_results,
                email_job_id=retry_email_job_id,
                error=str(e),
              )
          else:
            retry_email_payloads.update(
              self._build_retry_payloads_from_items(remaining_items)
            )
          break

        except smtplib.SMTPException as e:
          logger.exception(e)

          if is_last_attempt:
            self._mark_failed(
              email_job_results=email_job_results,
              email_job_id=email_job_id,
              error=str(e),
            )
          else:
            retry_email_payloads[email_job_id] = payload

        except Exception as e:
          logger.exception(e)
          raise EmailServiceError('Unexpected SMTP driver error.') from e

    except smtplib.SMTPException as e:
      logger.exception(e)

      if is_last_attempt:
        for email_job_id, _ in items:
          if email_job_id in email_job_results:
            continue
          self._mark_failed(
            email_job_results=email_job_results,
            email_job_id=email_job_id,
            error=str(e),
          )
      else:
        retry_email_payloads = dict(pending_email_payloads)

    except Exception as e:
      logger.exception(e)
      raise EmailServiceError('Unexpected SMTP driver error.') from e

    finally:
      try:
        connection.close()
      except Exception:
        logger.exception('Failed to close SMTP connection.')

    return retry_email_payloads

  def _send_one_email(
    self,
    connection,
    email_job_id: int,
    payload: EmailPayload,
  ) -> bool:
    sent_count = connection.send_messages([payload['message']])

    if sent_count != 1:
      logger.error(
        'SMTP send returned sent_count != 1. '
        f'email_job_id={email_job_id}, sent_count={sent_count}'
      )
      return False

    return True

  def _build_retry_payloads_from_items(
    self,
    items: list[tuple[int, EmailPayload]],
  ) -> dict[int, EmailPayload]:
    return {
      email_job_id: payload
      for email_job_id, payload in items
    }

  def _mark_failed(
    self,
    email_job_results: EmailJobResult,
    email_job_id: int,
    error: str,
  ) -> None:
    email_job_results[email_job_id] = {
      'state': EmailJob.State.FAILED,
      'error': error,
    }

  def _get_connection(self):
    try:
      return get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER or None,
        password=settings.EMAIL_HOST_PASSWORD or None,
        use_tls=settings.EMAIL_USE_TLS,
        use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
        fail_silently=False,
      )
    except Exception as e:
      logger.exception(e)
      raise EmailServiceError('Failed to initialize SMTP connection.') from e
