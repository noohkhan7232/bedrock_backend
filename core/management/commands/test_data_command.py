from django.core.management import call_command
from django.core.management.base import BaseCommand


class TestDataCommand(BaseCommand):
  def handle(self, *args, **options):
    if options['reset_db']:
      call_command('reset_db', '--noinput')
      call_command('migrate')

    self.sso = True if options['sso'] else False
    self.insert_data(*args, **options)

  def add_arguments(self, parser):
    parser.add_argument(
        '--unit_test', action='store_true', default=False,
        help='insert test data for unit data if True')
    parser.add_argument(
        '--reset_db', action='store_true',
        help='delete all db tables and re-create them.')
    parser.add_argument(
        '--seed', type=int, default=0,
        help='seed used to generate random number')
    parser.add_argument(
        '--sso', action='store_true', default=False,
        help='create new tenant for sso')

  def reset_db(self):
    call_command('reset_db', '--noinput')
    call_command('migrate')

  def insert_data(self, *args, **options):
    raise NotImplementedError('TestDataCommand.insert_data must be overwritten.')
