import sys

from core.dtos.sso import CreateSSOEmailDomainDTO
from core.management.commands.base import HybridCommand
from core.services.sso import create_sso_email_domain
from core.utils.email import ensure_valid_email_domain


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)
    parser.add_argument(
      '--domain',
      required=False,
      type=str,
      help='Email domain to register.',
    )
    parser.add_argument(
      '--connection_id',
      required=False,
      type=str,
      help='WorkOS connection ID.',
    )

  def handle(self, *args, **options):
    self.validate_options()

    domain = self.option_str(
      key='domain',
      prompt='Email domain to add: ',
      min_length=4,
      max_length=255,
      show_input=True,
    )
    connection_id = self.option_str(
      key='connection_id',
      prompt='Connection ID: ',
      min_length=4,
      max_length=255,
      show_input=False,
      echo=True,
    )

    domain = ensure_valid_email_domain(domain=domain)

    dto = CreateSSOEmailDomainDTO(domain=domain, connection_id=connection_id)
    create_sso_email_domain(dto=dto)

    if not self.is_automated:
      sys.stdout.write(f'Successfully registered domain:{domain} for SSO.\n')
