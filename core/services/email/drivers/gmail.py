import base64
import logging
import threading
from email.generator import BytesGenerator
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.auth.exceptions import (
  DefaultCredentialsError,
  GoogleAuthError,
  TransportError,
  RefreshError,
)
from google.oauth2.service_account import Credentials

from core.exceptions import EmailServiceError
from core.models import EmailJob
from core.services.email.drivers.base import (
  BaseEmailDriver,
  EmailPayload,
  EmailJobResult,
)

logger = logging.getLogger(__name__)


class GmailDriver(BaseEmailDriver):
  ATTEMPTS_MAX = 2

  service_account = settings.GOOGLE_SERVICE_ACCOUNT_PATH
  user = settings.EMAIL_HOST_USER
  scopes = ['https://www.googleapis.com/auth/gmail.send']

  _service = None
  _lock = threading.Lock()

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
    current_email_payloads = email_payloads

    for attempt in range(self.ATTEMPTS_MAX):
      retry_email_job_ids: set[int] = set()

      def on_result_callback(request_id, response, exception):
        email_job_id = int(request_id)
        state = EmailJob.State.DONE
        error = ''

        if exception is not None:
          logger.exception(
            f'Failed to send email (Request ID: {request_id}). '
            f'Error: {exception}'
          )
          state = EmailJob.State.FAILED
          error = str(exception)

          status = self._get_http_status(exc=exception)
          if status in (401, 403,):
            retry_email_job_ids.add(email_job_id)

        email_job_results[email_job_id] = {
          'state': state,
          'error': error,
        }

      try:
        service = self._get_service()
        batch_request = service.new_batch_http_request(
          callback=on_result_callback,
        )

        for email_job_id, payload in current_email_payloads.items():
          raw_message = self._get_raw_message(payload['message'])
          batch_request.add(
            service.users().messages().send(userId='me', body=raw_message),
            request_id=str(email_job_id),
          )
        batch_request.execute()
      except DefaultCredentialsError as e:
        logger.exception(e)
        raise EmailServiceError('Gmail credentials not found or invalid.') from e
      except RefreshError as e:
        if attempt >= self.ATTEMPTS_MAX - 1:
          logger.exception(e)
          raise EmailServiceError('Failed to obtain Gmail access token.') from e
        self._invalidate_service()
        continue
      except GoogleAuthError as e:
        logger.exception(e)
        raise EmailServiceError('Gmail auth failed.') from e
      except HttpError as e:
        status = self._get_http_status(exc=e)
        if status not in (401, 403) or attempt >= self.ATTEMPTS_MAX - 1:
          logger.exception(e)
          raise EmailServiceError('Gmail API request failed.') from e
        self._invalidate_service()
        continue
      except TransportError as e:
        logger.exception(e)
        raise EmailServiceError('Gmail API network/transport error.') from e
      except Exception as e:
        logger.exception(e)
        raise EmailServiceError('Unexpected Gmail driver error.') from e

      retry = len(retry_email_job_ids) > 0
      if retry:
        self._invalidate_service()
        current_email_payloads = {
          email_job_id: email_payload
          for email_job_id, email_payload in current_email_payloads.items()
          if email_job_id in retry_email_job_ids
        }
        continue
      else:
        break

    return email_job_results

  def _get_http_status(exc: Exception) -> int | None:
    if isinstance(exc, HttpError):
      return (
        getattr(exc, 'status_code', None)
        or getattr(getattr(exc, 'resp', None), 'status', None)
      )
    return None

  def _get_service(self):
    if self._service is not None:
      return self._service

    with self._lock:
      if self._service is not None:
        return self._service

      credentials = (
        Credentials
          .from_service_account_file(
            self.service_account,
            scopes=self.scopes,
          )
          .with_subject(self.user)
      )
      credentials.refresh(Request())

      self._service = build(
        'gmail',
        'v1',
        credentials=credentials,
        cache_discovery=False,
      )
      return self._service

  def _invalidate_service(self):
    with self._lock:
      self._service = None

  def _get_raw_message(self, message: EmailMultiAlternatives) -> dict:
    mimetext_message = message.message()
    raw_message = BytesIO()
    BytesGenerator(raw_message).flatten(mimetext_message)
    raw_message = base64.urlsafe_b64encode(raw_message.getvalue()).decode()
    return { 'raw': raw_message }
