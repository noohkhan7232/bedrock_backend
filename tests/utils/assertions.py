from typing import Any, Iterable, Mapping, Sequence, Union

from django.forms.models import model_to_dict
from django.db.models import Model, Q

from core.models import EmailJob


def assert_mapping_key(data: Mapping[str, Any], key: str) -> None:
  assert key in data, f'Missing key: {key!r}'

def assert_value_type(
    value: Any, expected_type: Union[type, Iterable[type]]) -> None:
  if not isinstance(expected_type, tuple):
    if isinstance(expected_type, type):
      expected_type = (expected_type,)
    elif isinstance(expected_type, Iterable):
      expected_type = tuple(expected_type)
    else:
      raise TypeError('expected_type must be a type or iterable of types')

  assert isinstance(value, expected_type), (
    f'Value {value!r} expected {expected_type}, got {type(value)}'
  )

def assert_value(value: Any, expected: Any, key: str = '') -> None:
  assert value == expected, f'{key}={value!r} expected {expected}'

def assert_numeric_range(
    value: int | float,
    key: str = '',
    min_value: int | float | None = None,
    max_value: int | float | None = None,
) -> None:
  if min_value is not None:
    assert value >= min_value, f'{key!r}={value} < min_value={min_value}'
  if max_value is not None:
    assert value <= max_value, f'{key!r}={value} > max_value={max_value}'

def assert_string_length(
    value: str,
    key: str = '',
    min_length: int | None = None,
    max_length: int | None = None,
) -> None:
  if min_length is not None:
    assert len(value) >= min_length, f'{key!r} length < min_length={min_length}'
  if max_length is not None:
    assert len(value) <= max_length, f'{key!r} length > max_length={max_length}'

def assert_mapping_value_type(
    data: Mapping[str, Any],
    key: str,
    expected_type: type | tuple[type, ...],
) -> None:
  assert_mapping_key(data=data, key=key)
  assert_value_type(value=data[key], expected_type=expected_type)

def assert_mapping_numeric_range(
    data: Mapping[str, Any],
    key: str,
    expected_type: type | tuple[type, ...] = (int, float,),
    min_value: int | None = None,
    max_value: int | None = None,
) -> None:
  assert_mapping_value_type(data=data, key=key, expected_type=expected_type)
  assert_numeric_range(
    value=data[key], key=key, min_value=min_value, max_value=max_value)

def assert_mapping_string_length(
    data: Mapping[str, Any],
    key: str,
    min_length: int | None = None,
    max_length: int | None = None,
) -> None:
  assert_mapping_value_type(data=data, key=key, expected_type=str)
  assert_string_length(
    value=data[key], key=key, min_length=min_length, max_length=max_length)

def assert_mapping_value(
    data: Mapping[str, Any],
    expected_type: type | tuple[type, ...],
    key: str = '',
    expected: int | float | str | bool | None = None,
) -> None:
  assert_mapping_value_type(data=data, key=key, expected_type=expected_type)
  assert data[key] == expected, f'{key}={data[key]!r} != {expected}.'

def assert_mapping_int(
    data: Mapping[str, Any],
    expected: int,
    key: str = '',
) -> None:
  assert_mapping_value(data=data, key=key, expected=expected, expected_type=int)

def assert_mapping_float(
    data: Mapping[str, Any],
    expected: float,
    key: str = '',
) -> None:
  assert_mapping_value(data=data, key=key, expected=expected, expected_type=float)

def assert_mapping_str(
    data: Mapping[str, Any],
    expected: str,
    key: str = '',
) -> None:
  assert_mapping_value(data=data, key=key, expected=expected, expected_type=str)

def assert_response_matches(
    data: Mapping[str, Any],
    expected: Mapping[str, Any] | Model,
    *,
    fields: Sequence[str] | None = None,
    excludes: Sequence[str] = [],
    allow_extra: bool = True,
    allow_missing: bool = True,
) -> None:
  """
  Compare `data` (typically `response.json()`) with `expected`, which can be
  either a dict-like object or any Django model instance.

  Parameters
  ----------
  data : Response payload (already a dict-like).
  expected : Dict-like OR Django model instance to compare against.
  allow_extra : True -> ignore keys that appear only in `data`.
  allow_missing : True -> ignore keys that appear only in `expected`.
  """
  assert_value_type(value=data, expected_type=dict)
  assert_value_type(value=expected, expected_type=(dict, Model,))

  expected_dict: Mapping[str, Any] = (
    model_to_dict(expected) if isinstance(expected, Model) else expected
  )

  if fields is None:
    keys_to_check = data.keys() & expected_dict.keys()
  else:
    missing = set(fields) - data.keys()
    assert not missing, f'Missing field(s) in response: {missing!r}'
    keys_to_check = fields

  keys_to_check = [key for key in keys_to_check if key not in excludes]

  for key in keys_to_check:
    assert_value(value=data[key], expected=expected_dict[key], key=key)

  data_items = data.items()
  expected_items = expected_dict.items()

  if not allow_missing:
    missing = expected_items - data_items
    assert not missing, f'Missing key/value(s) in resposne: {missing!r}'
  if not allow_extra:
    extra = data_items - expected_items
    assert not extra, f'Unexpected extra key/value(s) in response: {extra!r}'

def assert_email_jobs_created(
    email_type: EmailJob.EmailType,
    to_emails: list[str],
    tenant_id: int | None = None,
    expected_count: int = 0,
) -> None:
  query = (
    EmailJob.objects
      .filter(
        email_type=email_type,
        to_email__in=to_emails,
      )
  )
  if tenant_id is not None:
    query = query.filter(tenant_id=tenant_id)

  count = query.count()
  assert count == expected_count
  if expected_count > 0:
    query = (
      query
        .filter(state=EmailJob.State.PENDING)
        .exclude(Q(dedupe_key__isnull=True) | Q(dedupe_key=''))
    )
    assert count == query.count()

def assert_email_job_created(
    email_type: EmailJob.EmailType,
    to_email: str,
    tenant_id: int | None = None,
) -> None:
  query = (
    EmailJob.objects
      .filter(
        email_type=email_type,
        to_email=to_email,
      )
  )
  if tenant_id is not None:
    query = query.filter(tenant_id=tenant_id)

  assert query.count() == 1
  email_job = query.get()
  assert email_job.state == EmailJob.State.PENDING
  assert len(email_job.dedupe_key) > 0

def assert_email_job_not_created(
    email_type: EmailJob.EmailType,
    to_email: str,
    tenant_id: int | None = None,
) -> None:
  query = (
    EmailJob.objects
      .filter(
        email_type=email_type,
        to_email=to_email,
      )
  )
  if tenant_id is not None:
    query = query.filter(tenant_id=tenant_id)

  assert query.count() == 0
