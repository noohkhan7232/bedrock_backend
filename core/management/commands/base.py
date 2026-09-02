from datetime import datetime
from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from core.utils.text import normalize


class HybridCommand(BaseCommand):
  _options: dict[str, str | int | bool | None]
  _added_option_keys: set[str]

  BATCH_SIZE = 500

  def execute(self, *args, **options):
    self._options = options
    return super().execute(*args, **options)

  def add_arguments(self, parser) -> None:
    self._added_option_keys = set()

    _add_argument = parser.add_argument
    def custom_add_argument(*args, **kwargs):
      action = _add_argument(*args, **kwargs)
      self._added_option_keys.add(action.dest)
      return action

    parser.add_argument = custom_add_argument

    parser.add_argument(
      '--automation',
      action='store_true',
      help='Run non-interactively; require all necessary arguments.'
    )

  def validate_options(self):
    if self.is_automated:
      return

    ignored = {'automation'}
    for key in self._added_option_keys:
      if key in ignored:
        continue
      if self._options.get(key) is not None:
        raise CommandError(f'--{key} cannot be used without --automation.')

  def parse_date(self, date_str: str):
    if date_str is None or date_str == '':
      return None

    try:
      return datetime.strptime(date_str, '%m-%d-%Y').date()
    except ValueError:
      raise CommandError('Date must be in MM-DD-YYYY format')

  def option_str(
    self, key: str,
    prompt: str,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    choices: list[str] | None = None,
    show_input: bool = False,
    echo: bool = False,
  ) -> str | None:
    value = None

    if self.is_automated:
      value: str | None = self._options.get(key)
    elif show_input:
      value: str = input(prompt)
    elif echo:
      value: str = getpass(prompt, echo_char='*')
    else:
      value: str = getpass(prompt)

    if (
      min_length is None
      and max_length is None
      and length is None
      and choices is None
    ):
      if value is None:
        return None

      if isinstance(value, str) and value.strip() == '':
        return None

    if not isinstance(value, str):
      raise CommandError(f'Option "{key}" must be a string.')

    value = value.strip()

    normalized_value = normalize(value)
    if normalized_value != value:
      raise CommandError(
        f'Option "{key}" contains invalid or non-canonical characters.'
      )

    if min_length is not None and len(value) < min_length:
      raise CommandError(
        f'Option "{key}" length must be >= {min_length}.'
      )
    if max_length is not None and len(value) > max_length:
      raise CommandError(
        f'Option "{key}" length must be <= {max_length}.'
      )
    if length is not None and len(value) != length:
      raise CommandError(
        f'Option "{key}" length must be {length}.'
      )
    if choices is not None and value not in choices:
      raise CommandError(
        f'Option "{key}" must be in {choices}.'
      )

    return value or None

  def option_int(
    self, key: str,
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
    choices: list[int] | None = None,
  ) -> int | None:
    value = None

    if self.is_automated:
      value: int | None = self._options.get(key)
    else:
      value: str = input(prompt)

    if isinstance(value, str) and value.strip() == '':
      if min_value is not None or max_value is not None or choices:
        raise CommandError(f'Option "{key}" must be int.')
      return None

    if isinstance(value, bool):
      raise CommandError(f'Option "{key}" must be int.')

    try:
      value = int(value)
    except (ValueError, TypeError,) as e:
      raise CommandError(f'Option "{key}" must be int.') from e

    if min_value is not None and value < min_value:
      raise CommandError(f'Option "{key}" must be >= {min_value}.')
    if max_value is not None and value > max_value:
      raise CommandError(f'Option "{key}" must be <= {max_value}.')
    if choices is not None and value not in choices:
      raise CommandError(f'Option "{key}" must be in {choices}.')

    return value

  @property
  def is_automated(self) -> bool:
    return bool(self._options.get('automation'))
