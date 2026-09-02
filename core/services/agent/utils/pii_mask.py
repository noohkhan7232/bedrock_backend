import re
from typing import List, Tuple


class SimplePIIMasker:
  """
  PII Masking without Microsoft Presidio.
  For MVP, mask credit card number and SSN.
  """
  def __init__(self):
    self.patterns: List[Tuple[re.Pattern, str]] = [
      (
        re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
        '[CREDIT_CARD_NUM]'
      ),
      (
        re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        '[US_SSN]'
      ),
    ]

  def mask(self, text: str) -> str:
    """
    Assume the given text is enough sanitized(spaces, ctrl letter, wide)
    """
    if not text:
      return text

    masked_text = text
    for pattern, replacement in self.patterns:
      masked_text = pattern.sub(replacement, masked_text)

    return masked_text


pii_masker = SimplePIIMasker()
