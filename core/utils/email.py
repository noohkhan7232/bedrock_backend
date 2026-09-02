import hashlib
import json
import re
import unicodedata
import urllib.parse

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email

from core.exceptions import DomainValidationError
from core.utils.text import normalize


LOCAL_PART_ASCII_RE = re.compile(
  r"(?!\.)(?!.*\.\.)[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}(?<!\.)\Z"
)
DOMAIN_LABEL_RE = re.compile(
  r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
)


def normalize_email(email: str) -> str:
  return unicodedata.normalize('NFKC', email).strip().lower()


def normalize_email_domain(domain: str) -> str:
  domain = (
    unicodedata.normalize('NFKC', domain.strip().strip('.').strip('@')).lower()
  )
  return domain


def ensure_valid_email_domain(domain: str) -> str:
  domain = normalize_email_domain(domain)

  if not domain:
    raise ValueError('Empty email domain.')
  if len(domain) > 200:
    raise ValueError('Too long email domain.')
  if '..' in domain:
    raise ValueError('Consecutive dots not allowed.')

  labels = domain.split('.')
  if len(labels) < 2:
    raise ValueError('Domain must contain at least 1 dot.')
  for label in labels:
    if not DOMAIN_LABEL_RE.match(label):
      raise ValueError(
        f'Non-ASCII domain label is not supported. label: {label}')

  return domain


def get_email_domain(email: str) -> str:
  email = normalize(email)

  if email.count('@') != 1:
    raise ValueError('Invalid email address.')

  _, _, domain = email.rpartition('@')
  return ensure_valid_email_domain(domain)


def ensure_valid_email(email: str) -> str:
  email = normalize(email)

  try:
    django_validate_email(email)
  except DjangoValidationError as e:
    raise DomainValidationError('; '.join(e.messages))
  except Exception as e:
    raise DomainValidationError(e)

  local, _, domain = email.rpartition('@')

  if not LOCAL_PART_ASCII_RE.fullmatch(local):
    raise DomainValidationError('Invalid local-part: must be ASCII dot-atom.')

  domain = ensure_valid_email_domain(domain)
  return normalize_email(f'{local}@{domain}')


def generate_dedupe_key(
  email_type: str,
  to_email: str,
  tenant_id: int | None,
  options: dict | None = None,
) -> str:
  semantic = {
    'to_email': to_email.strip().lower(),
  }

  if options is not None:
    if not isinstance(options, dict):
      raise ValueError('options must be dict')
    semantic['options'] = options

  raw = (
    json
      .dumps(semantic, separators=(',', ':'), sort_keys=True)
      .encode('utf-8')
  )
  h = hashlib.sha256(raw).hexdigest()[:12]
  tenant_part = 'none' if tenant_id is None else str(tenant_id)
  return f'v1:{email_type}:{tenant_part}:{h}'


def get_queued_email_custom_identifier(tenant_id, email_type):
  return f'{"" if tenant_id is None else str(tenant_id)}-{str(email_type)}'


def dict_to_url_params(obj, indent=0, encode='utf8'):
  return urllib.parse.quote(json.dumps(obj, indent=indent).encode(encode))
