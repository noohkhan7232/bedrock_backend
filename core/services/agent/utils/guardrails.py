from typing import Optional

from core.exceptions import ContentPolicyViolationError
from core.services.agent.clients.openai import client


def validate_input(text: str, raise_exception: bool = False):
  resp = client.moderations.create(
    model='omni-moderation-latest',
    input=text,
  )
  if resp.results[0].flagged:
    if raise_exception:
      raise ContentPolicyViolationError('Input text violates the content policy.')
    return False
  return text if raise_exception else True


def is_blank_text(text: Optional[str]) -> bool:
  if text is None:
    return True
  return text.strip() == ''
