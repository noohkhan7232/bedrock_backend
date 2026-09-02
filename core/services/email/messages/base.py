import os
from abc import ABC, abstractmethod
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q

from core.constants import CONSTANTS
from core.models import EmailJob, Tenant, TenantUser, User


class BaseTemplateMessage(ABC):
  app_name = settings.APP_NAME
  base_url = settings.CLIENT_URL
  from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
  template_dir = settings.EMAIL_TEMPLATE_DIR

  _HELP_CENTER_URL = CONSTANTS.CONTACTS.HELP_CENTER_URL
  _LANDING_PAGE_URL = CONSTANTS.CONTACTS.LANDING_PAGE_URL
  _TERMS_OF_SERVICE_URL = CONSTANTS.CONTACTS.TERMS_OF_SERVICE_URL
  _PRIVACY_POLICY_URL = CONSTANTS.CONTACTS.PRIVACY_POLICY_URL
  _CALIFORNIA_NOTICE_URL = CONSTANTS.CONTACTS.CALIFORNIA_NOTICE_URL
  _SERVICE_OWNER_ADDRESS = CONSTANTS.CONTACTS.SERVICE_OWNER_ADDRESS

  tenant_required = False
  sender_user_required = False

  tenant = None
  sender_user = None

  message = None

  def __init__(self, email_job: EmailJob):
    self.validate_context(
      tenant=email_job.tenant,
      sender_user=email_job.sender_user,
    )
    self.validate_template_vars(template_vars=email_job.template_vars)
    self.message = self.build_message(email_job=email_job)

  @abstractmethod
  def get_html(self, email_job: EmailJob) -> str:
    pass

  @abstractmethod
  def get_plain_text(self, email_job: EmailJob) -> str:
    pass

  @abstractmethod
  def get_subject(self, email_job: EmailJob) -> str:
    pass

  @abstractmethod
  def validate_template_vars(self, template_vars) -> None:
    pass

  def get_plain_text_footer(self, short=False) -> str:
    return (
      f'{"-"*64}\n'
      f'Learn more: {self._LANDING_PAGE_URL}\n'
      f'{self._SERVICE_OWNER_ADDRESS}'
    ) if short else (
      f'{"-"*64}\n'
      f'What is {settings.APP_NAME}?\n'
      f'{settings.APP_NAME} helps your team be more connected through '
      f'collaborative skills management, internal expert search, and '
      f'communication records.\n'
      f'Learn more: {self._LANDING_PAGE_URL}\n\n'
      f'{self._SERVICE_OWNER_ADDRESS}'
    )

  def build_message(self, email_job: EmailJob) -> EmailMultiAlternatives:
    subject = self.get_subject(email_job=email_job)
    plain_text = self.get_plain_text(email_job=email_job)
    html = self.get_html(email_job=email_job)

    message = EmailMultiAlternatives(
      subject=subject,
      body=plain_text,
      from_email=self.from_email,
      to=[email_job.to_email],
    )
    message.attach_alternative(html, 'text/html')

    return message

  def get_email_asset_url(self, path: str) -> str:
    base_url = settings.EMAIL_ASSET_BASE_URL.rstrip('/')
    return f'{base_url}/{path.lstrip('/')}'

  def get_logo_image_url(self, filename: str = 'logo.png') -> str:
    return self.get_email_asset_url(path=filename)

  def get_html_path(self) -> str:
    return os.path.join(self.template_dir, self.template_name)

  def get_sender_user_from(self, email_job: EmailJob) -> User:
    if email_job.sender_user is None:
      raise ValueError('User associated with the email job is None.')
    return email_job.sender_user

  def get_tenant_from(self, email_job: EmailJob) -> Tenant:
    if email_job.tenant is None:
      raise ValueError('Tenant associated with the email job is None.')
    return email_job.tenant

  def get_url(self, path: str, query_params: dict | None) -> str:
    encoded_query_params = (
      None if query_params is None else urlencode(query_params)
    )
    url = os.path.join(self.base_url, path)
    if encoded_query_params is None:
      return url
    return f'{url}?{encoded_query_params}'

  def get_user_name(self, user: User) -> str:
    return f'{user.first_name} {user.last_name}'

  def validate_context(
    self,
    tenant: Tenant | None,
    sender_user: User | None,
  ) -> None:
    if self.tenant_required and not isinstance(tenant, Tenant):
      raise ValueError('Invalid tenant found.')
    if self.sender_user_required and not isinstance(sender_user, User):
      raise ValueError('Invalid sender_user found')

    if (tenant is not None) and (sender_user is not None):
      cond = Q(tenant_id=tenant.id, user_id=sender_user.id)
      # Use objects: sender must belong to the tenant,
      # even if the membership is inactive.
      if not TenantUser.objects.filter(cond).exists():
        raise ValueError('TenantUser not found.')
