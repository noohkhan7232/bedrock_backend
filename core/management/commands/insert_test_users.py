import random
import sys

from core.management.commands.base import HybridCommand
from core.services.test_data.user import create_test_users


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
      '--count',
      required=False,
      type=int,
      help='The number of users',
    )

  def init_params(self):
    self.seed = self.option_int(
      key='seed',
      prompt='Optional random seed(integer): ',
    ) or 0
    self.count = self.option_int(
      key='count',
      prompt='The number of users: ',
      min_value=0,
      max_value=1000,
    ) or 0

  def handle(self, *args, **options):
    self.validate_options()
    self.init_params()

    rng = random.Random(self.seed)

    users = create_test_users(
      rng=rng,
      count=self.count,
      batch_size=self.BATCH_SIZE,
    )

    sys.stdout.write(f'Created {len(users)} users.\n')
