import sys

from core.management.commands.base import HybridCommand
from core.models import SSOEmailDomain


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)
    parser.add_argument(
      '--domain',
      required=False,
      type=str,
      help='Email domain to unregister.',
    )
    parser.add_argument(
      '--connection_id',
      required=False,
      type=str,
      help='Connection ID to unregister.',
    )

  def handle(self, *args, **options):
    self.validate_options()

    domain = self.option_str(
      key='domain',
      prompt='Email domain to delete (Optional): ',
      show_input=True,
    )
    if domain is not None:
      self.delete_by_domain(domain=domain)
      sys.stdout.write(f'Successfully unregistered {domain}.\n')
      return

    connection_id = self.option_str(
      key='connection_id',
      prompt='Connection ID to delete: ',
      min_length=4,
      max_length=255,
      show_input=False,
      echo=True,
    )
    self.delete_by_connection_id(connection_id=connection_id)

  def delete_by_domain(self, domain: str):
    sso_email_domain = SSOEmailDomain.all_objects.get(domain__exact=domain)
    sso_email_domain.delete()

  def delete_by_connection_id(self, connection_id: str):
    sso_email_domains = SSOEmailDomain.all_objects.filter(
      connection_id=connection_id,
    )
    count = sso_email_domains.count()
    sso_email_domains.delete()
    sys.stdout.write(f'Successfully unregistered {count} email domain(s).\n')


