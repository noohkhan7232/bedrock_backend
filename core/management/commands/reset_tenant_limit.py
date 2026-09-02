import sys

from django.conf import settings
from django.core.management.base import CommandError

from core.management.commands.base import HybridCommand
from core.models import Tenant
from core.services.tenant_limit_override import reset_tenant_limit


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)

    parser.add_argument(
      '--domain',
      required=False,
      type=str,
      help='Tenant domain',
    )
    parser.add_argument(
      '--limit_key',
      required=False,
      type=str,
      default=None,
      help='Limit key',
    )

  def init_params(self):
    self.domain = self.option_str(
      key='domain',
      prompt='Tenant domain: ',
      length=settings.TENANT_DOMAIN_LENGTH,
      show_input=False,
      echo=True,
    )
    self.limit_key = self.option_str(
      key='limit_key',
      prompt='Limit key: ',
      show_input=True,
      min_length=1,
      max_length=64,
    )

  def handle(self, *args, **options):
    self.validate_options()
    self.init_params()

    try:
      tenant = Tenant.objects.get(domain=self.domain)
    except Tenant.DoesNotExist:
      raise CommandError('Tenant not found.')

    reset = reset_tenant_limit(tenant_id=tenant.id, limit_key=self.limit_key)

    if reset:
      sys.stdout.write(
        f'Reset override {self.limit_key} for {tenant.name}.\n'
      )
    else:
      sys.stdout.write(
        f'No override found for {self.limit_key} on {tenant.name}; '
        'already using the plan default.\n'
      )
