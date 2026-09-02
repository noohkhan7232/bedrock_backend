from django.core.management import call_command

from core.management.commands.base import HybridCommand


class Command(HybridCommand):
  def add_arguments(self, parser):
    super().add_arguments(parser=parser)

    parser.add_argument(
      '--reset_db',
      required=False,
      type=str,
      help='delete all db tables and re-create them.',
    )
    parser.add_argument(
      '--seed',
      required=False,
      type=int,
      help='Optional random seed(integer)',
    )

  def init_params(self):
    self.reset_db = self.option_str(
      key='reset_db',
      prompt='Reset DB(yes or no): ',
      show_input=True,
      echo=True,
    ) or 'no'
    self.seed = self.option_int(
      key='seed',
      prompt='Optional random seed(integer): ',
    ) or 0

  def handle(self, *args, **options):
    self.validate_options()
    self.init_params()

    self._init_db()
    self._insert_users()
    self._insert_tenants()

  def _init_db(self):
    if self.reset_db == 'yes':
      call_command('reset_db', '--noinput')
      call_command('migrate')

  def _insert_users(self):
    call_command('insert_test_users')

  def _insert_tenants(self):
    call_command('insert_test_tenant')

  def _insert_tenant_users(self):
    call_command('insert_test_tenant_users')
