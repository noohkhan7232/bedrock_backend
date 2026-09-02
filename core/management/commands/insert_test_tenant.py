import random
import sys

from core.constants import PLANS
from core.management.commands.base import HybridCommand
from core.services.test_data.tenant import create_test_tenant


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
      '--plan_uid',
      required=False,
      type=int,
      help='Plan uid of tenant',
    )
    parser.add_argument(
      '--admin_user_id',
      required=False,
      type=int,
      help='User ID of tenant admin',
    )

  def init_params(self):
    self.seed = self.option_int(
      key='seed',
      prompt='Optional random seed(integer): ',
    ) or 0
    self.plan_uid = self.option_int(
      key='plan_uid',
      prompt='Tenant plan uid: ',
    ) or PLANS.FREE.uid
    self.admin_user_id = self.option_int(
      key='admin_user_id',
      prompt='User ID of tenant admin: ',
    ) or None

  def handle(self, *args, **options):
    self.validate_options()
    self.init_params()

    rng = random.Random(self.seed)

    tenant = create_test_tenant(
      rng=rng,
      admin_user_id=self.admin_user_id,
      plan_uid=self.plan_uid,
    )

    sys.stdout.write(f'Created tenant: {tenant.name}.\n')
