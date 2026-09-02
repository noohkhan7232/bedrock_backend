from django.conf import settings

from core.services.email.messages.base import BaseTemplateMessage
from core.models import EmailJob


class EmailVerificationMessage(BaseTemplateMessage):
  expiration_hours = settings.EMAIL_VERIFICATION_CODE_LIFETIME_HOURS
  template_name = 'email_verification.html'

  tenant_required = False
  sender_user_required = False

  def get_html(self, email_job: EmailJob) -> str:
    html_path = self.get_html_path()
    url = self.get_url(email_job=email_job)

    with open(html_path, encoding='utf-8') as f:
      html = str(f.read())

    return (
      html
        .replace('__APP_NAME__', str(self.app_name))\
        .replace('__EXPIRATION_HOURS__', str(self.expiration_hours))
        .replace('__LANDING_PAGE_URL__', self._LANDING_PAGE_URL)
        .replace('__LOGO_IMAGE_URL__', self.get_logo_image_url())
        .replace('__TERMS_OF_SERVICE_URL__', self._TERMS_OF_SERVICE_URL)
        .replace('__PRIVACY_POLICY_URL__', self._PRIVACY_POLICY_URL)
        .replace('__CALIFORNIA_NOTICE_URL__', self._CALIFORNIA_NOTICE_URL)
        .replace('__SERVICE_OWNER_ADDRESS__', self._SERVICE_OWNER_ADDRESS)
        .replace('__USER_SIGNUP_URL__', url)
    )

  def get_plain_text(self, email_job: EmailJob) -> str:
    url = self.get_url(email_job=email_job)

    return (
      f'You are almost there!\n\n'
      f'Please click the link below to verify your email address.\n'
      f'{url}\n\n'
      f'For security purpose, the above link will expire in '
      f'{self.expiration_hours} hours.\n'
      f'By clicking this link, you are agreeing to our '
      f'Terms of Service({self._TERMS_OF_SERVICE_URL}) '
      f'and Privacy Policy({self._PRIVACY_POLICY_URL}).\n'
      f'California Notice at Collection can be found '
      f'here({self._CALIFORNIA_NOTICE_URL}).\n\n'
      f'Please ignore this email if you are not sure why you received it.\n'
      f'{self.get_plain_text_footer(short=False)}'
    )


  def get_subject(self, email_job: EmailJob) -> str:
    return 'Please verify your email'

  def validate_template_vars(self, template_vars) -> None:
    if template_vars.get('verification_code') is None:
      raise ValueError('Valid code not found.')

  def get_url(self, email_job: EmailJob) -> str:
    query_params = {
      'verification_code': email_job.template_vars.get('verification_code'),
    }
    return super().get_url(path='auth/signup', query_params=query_params)
