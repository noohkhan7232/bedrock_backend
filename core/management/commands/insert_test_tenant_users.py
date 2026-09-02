import random
import sys

from django.conf import settings

from core.management.commands.base import HybridCommand
from core.services.test_data.tenant_user import create_test_tenant_users


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)

    parser.add_argument(
      '--seed',
      required=False,
      type=int,
      help='Optional random seed(integer)',
    )
    parser.add_argument(
      '--domain',
      required=False,
      type=str,
      help='Tenant domain',
    )
    parser.add_argument(
      '--count',
      required=False,
      type=int,
      help='The number of tenant users',
    )
    parser.add_argument(
      '--admins_count',
      required=False,
      type=int,
      help='The number of extra admins',
    )
    parser.add_argument(
      '--managers_count',
      required=False,
      type=int,
      help='The number of managers',
    )

  def init_params(self):
    self.seed = self.option_int(
      key='seed',
      prompt='Optional random seed(integer): ',
    ) or 0
    self.domain = self.option_str(
      key='domain',
      prompt='Tenant domain: ',
      length=settings.TENANT_DOMAIN_LENGTH,
      show_input=False,
      echo=True,
    )
    self.count = self.option_int(
      key='count',
      prompt='The number of tenant users: ',
      min_value=0,
      max_value=1000,
    ) or 0
    self.admins_count = self.option_int(
      key='admins_count',
      prompt='The number of extra admins: ',
      min_value=0,
      max_value=999,
    ) or 0
    self.managers_count = self.option_int(
      key='count',
      prompt='The number of managers: ',
      min_value=0,
      max_value=1000,
    )

  def handle(self, *args, **options):
    self.validate_options()
    self.init_params()

    rng = random.Random(self.seed)

    tenant_users = create_test_tenant_users(
      rng=rng,
      tenant_domain=self.domain,
      count=self.count,
      admins_count=self.admins_count,
      managers_count=self.managers_count,
    )

    sys.stdout.write(f'Created {len(tenant_users)} tenant users.\n')
