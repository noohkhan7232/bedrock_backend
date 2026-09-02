import json

from core.constants import PLANS
from core.services.subscription import get_tenant_plan_uid
from .sanitize import (
  normalize_unicode,
  sanitize_chars,
  break_code_fences
)


def _sanitize_text(text: str) -> str:
  text = normalize_unicode(text=text)
  text = sanitize_chars(text=text)
  text = break_code_fences(text=text)
  return text


def _get_user_profile(user) -> dict:
  return {
    'first_name': _sanitize_text(user.first_name),
    'last_name': _sanitize_text(user.last_name),
    'location': _sanitize_text(user.location),
    'locale': _sanitize_text(user.locale),
  }


def _get_tenant_profile(tenant) -> dict:
  plan_uid = get_tenant_plan_uid(tenant_id=tenant.id)
  plan = PLANS.get_by_uid(uid=plan_uid)
  return {
    'name': _sanitize_text(tenant.name),
    'plan': plan.name,
  }


def serialize_user_profile_for_prompt(user) -> str:
  return json.dumps(
    _get_user_profile(user=user), ensure_ascii=False, separators=(',', ':')
  )


def serialize_tenant_user_profile_for_prompt(tenant_user) -> str:
  user_profile = _get_user_profile(user=tenant_user.user)
  tenant_profile = _get_tenant_profile(tenant=tenant_user.tenant)
  profile = {
    'user': {
      **user_profile,
      'title': _sanitize_text(tenant_user.title),
    },
    'tenant': tenant_profile,
  }

  return json.dumps(profile, ensure_ascii=False, separators=(',', ':'))


def get_user_prompt(
  use_profile: bool = False,
  use_context: bool = False,
) -> str:
  user_prompt = ''

  if use_profile:
    user_prompt += '### PROFILE (JSON):\n```json\n{profile_json}\n```\n'
  if use_context:
    user_prompt += '### CONTEXT:\n```text\n{context}\n```\n'
  user_prompt += '### USER QUESTION:\n{input}'

  return user_prompt
