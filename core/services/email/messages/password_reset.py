from django.conf import settings

from core.services.email.messages.base import BaseTemplateMessage
from core.models import EmailJob


class PasswordResetMessage(BaseTemplateMessage):
  expiration_hours = settings.PASSWORD_RESET_CODE_LIFETIME_HOURS
  template_name = 'password_reset.html'

  tenant_required = False
  sender_user_required = False

  def get_html(self, email_job: EmailJob) -> str:
    html_path = self.get_html_path()
    url = self.get_url(email_job=email_job)

    with open(html_path, encoding='utf-8') as f:
      html = str(f.read())

    return (
      html
        .replace('__APP_NAME__', self.app_name)
        .replace('__EXPIRATION_HOURS__', str(self.expiration_hours))
        .replace('__LANDING_PAGE_URL__', self._LANDING_PAGE_URL)
        .replace('__LOGO_IMAGE_URL__', self.get_logo_image_url())
        .replace('__SERVICE_OWNER_ADDRESS__', self._SERVICE_OWNER_ADDRESS)
        .replace('__PASSWORD_RESET_URL__', url)
    )

  def get_plain_text(self, email_job: EmailJob) -> str:
    url = self.get_url(email_job=email_job)

    return (
      f'We have received a request to reset your password on your '
      f'{self.app_name} account.\n'
      f'To confirm and set your new password, please click the link below:\n'
      f'{url}\n\n'
      f'For security purpose, the above link will expire in '
      f'{self.expiration_hours} hours.\n'
      f'Please ignore this email if you are not sure why you received it.\n'
      f'{self.get_plain_text_footer(short=False)}'
    )

  def get_subject(self, email_job: EmailJob) -> str:
    return f'{self.app_name} password reset'

  def validate_template_vars(self, template_vars) -> None:
    if template_vars.get('reset_code') is None:
      raise ValueError('Valid code not found.')

  def get_url(self, email_job: EmailJob) -> str:
    query_params = {
      'password_reset_code': email_job.template_vars.get('reset_code'),
    }
    return super().get_url(
      path='auth/reset/password',
      query_params=query_params,
    )
