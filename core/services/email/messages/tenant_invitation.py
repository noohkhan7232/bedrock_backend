from django.conf import settings

from core.services.email.messages.base import BaseTemplateMessage
from core.models import EmailJob


class TenantInvitationMessage(BaseTemplateMessage):
  expiration_hours = settings.TENANT_INVITATION_CODE_LIFETIME_HOURS
  template_name = 'tenant_invitation.html'

  tenant_required = True
  sender_user_required = True

  def get_html(self, email_job: EmailJob) -> str:
    html_path = self.get_html_path()
    tenant = self.get_tenant_from(email_job=email_job)
    sender_user = self.get_sender_user_from(email_job=email_job)
    sender_name = self.get_user_name(user=sender_user)
    sender_email = sender_user.email
    url = self.get_url(email_job=email_job)

    with open(html_path, encoding='utf-8') as f:
      html = str(f.read())

    return (
      html
        .replace('__TENANT_NAME__', tenant.name)
        .replace('__APP_NAME__', self.app_name)
        .replace('__INVITER_NAME__', sender_name)
        .replace('__INVITER_EMAIL__', sender_email)
        .replace('__EXPIRATION_HOURS__', str(self.expiration_hours))
        .replace('__LANDING_PAGE_URL__', self._LANDING_PAGE_URL)
        .replace('__LOGO_IMAGE_URL__', self.get_logo_image_url())
        .replace('__SERVICE_OWNER_ADDRESS__', self._SERVICE_OWNER_ADDRESS)
        .replace('__TENANT_USER_SIGNUP_URL__', url)
    )

  def get_plain_text(self, email_job: EmailJob) -> str:
    sender_user = self.get_sender_user_from(email_job=email_job)
    sender_name = self.get_user_name(user=sender_user)
    sender_email = sender_user.email
    tenant = self.get_tenant_from(email_job=email_job)
    url = self.get_url(email_job=email_job)

    return (
      f'You are invited to {tenant.name} on {self.app_name}!\n\n'
      f'{sender_name} ({sender_email}) has invited you to '
      f'{tenant.name} workspace on {self.app_name}.\n'
      f'To accept the invitation, please click the link below.\n'
      f'{url}\n\n'
      f'For security purpose, the above link will expire in '
      f'{self.expiration_hours} hours.\n'
      f'Not sure why you received this email? Please contact '
      f'{sender_email}.\n\n'
      f'{self.get_plain_text_footer(short=False)}'
    )

  def get_subject(self, email_job: EmailJob) -> str:
    sender_user = self.get_sender_user_from(email_job=email_job)
    sender_name = self.get_user_name(user=sender_user)

    return (
      f'{sender_name} has invited you '
      f'to join the workspace in {self.app_name}'
    )

  def validate_template_vars(self, template_vars) -> None:
    if template_vars.get('invitation_code') is None:
      raise ValueError('Valid code not found.')

  def get_url(self, email_job: EmailJob) -> str:
    query_params = {
      'invitation_code': email_job.template_vars.get('invitation_code'),
    }
    return super().get_url(path='auth/signup', query_params=query_params)

