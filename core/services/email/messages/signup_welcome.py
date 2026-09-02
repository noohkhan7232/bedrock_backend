from core.services.email.messages.base import BaseTemplateMessage
from core.models import EmailJob


class SignupWelcomeMessage(BaseTemplateMessage):
  template_name = 'signup_welcome.html'

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
        .replace('__HELP_CENTER_URL__', self._HELP_CENTER_URL)
        .replace('__LANDING_PAGE_URL__', self._LANDING_PAGE_URL)
        .replace('__LOGO_IMAGE_URL__', self.get_logo_image_url())
        .replace('__SERVICE_OWNER_ADDRESS__', self._SERVICE_OWNER_ADDRESS)
        .replace('__APP_HOME_URL__', url)
    )

  def get_plain_text(self, email_job: EmailJob) -> str:
    url = self.get_url(email_job=email_job)

    return (
      f'Welcome to {self.app_name}!\n'
      f'We are so grateful you are here.\n\n'
      f'{self.app_name} helps your team be more connected through '
      f'collaborative skills management, internal expert search, '
      f'and communication records.\n\n'
      f'Here are the steps to get started.\n\n'
      f'1. Complete your profile.\n'
      f'Upload your photo. Add your title, location '
      f'and links to help coworkers know you better.\n'
      f'HINT: Add a Calendly link for virtual office hours.\n\n'
      f'2. Add skills.\n'
      f'Add skills on your skills graph. Also, '
      f'try adding skills to your coworkers!\n'
      f'HINT: Using shorter skill name will improve the readability '
      f'of skills graph e.g. AWS instead of Amazon Web Services.\n\n'
      f'3. Search experts.\n'
      f'Type in what you need help with and find the right experts!\n'
      f'HINT: You can search using skill name or first & last name.\n\n'
      f'4. Create a record.\n'
      f'Once you reached out to someone or vice versa, '
      f'create a record to measure connections inside your team.\n'
      f'HINT: Add saved hours when you felt you saved your time '
      f'by talking with this person.\n\n'
      f'Get Started from here: {url}\n\n'
      f'{self.get_plain_text_footer(short=True)}'
    )

  def get_subject(self, email_job: EmailJob) -> str:
    return f'Welcome to {self.app_name}'

  def validate_template_vars(self, template_vars) -> None:
    pass

  def get_url(self, email_job: EmailJob) -> str:
    return super().get_url(
      path='auth/verification/email/login',
      query_params=None,
    )
