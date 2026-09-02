import tiktoken
from lingua import LanguageDetectorBuilder

from core.constants.language import APP_LANGUAGES


_language_detector = None
_encoding_name = 'o200k_base'
_encoding = tiktoken.get_encoding(_encoding_name)

TARGET_LANGUAGES = [
  lang['lingua'] for lang in APP_LANGUAGES
  if lang.get('lingua', None) is not None
]


def get_language_detector():
  global _language_detector
  if _language_detector is None:
    _language_detector = (
      LanguageDetectorBuilder
        .from_languages(*TARGET_LANGUAGES)
        .build()
    )
  return _language_detector


def detect_language_code(
  text: str,
  fallback_code: str = 'en',
  fallback_name: str = 'English'
) -> tuple[str, str, float]:
  detector = get_language_detector()
  language = detector.detect_language_of(text)

  code = fallback_code
  name = fallback_name
  confidence = 0.0

  if language:
    code = (
      language.iso_code_639_1.name.lower()
      if getattr(language, 'iso_code_639_1', None)
      else language.iso_code_639_3.name.lower()
    )
    name = language.name.replace('_', ' ').title()
    confidence = detector.compute_language_confidence(text, language)
  return code, name, confidence


def count_tokens(text: str) -> int:
  if not text:
    return 0
  tokens = _encoding.encode(text)
  return len(tokens)


def truncate_text_by_tokens(
  text: str,
  max_tokens: int = 2000,
  keep_tail: bool = True,
) -> str:
  try:
    tokens = _encoding.encode(text)
    if len(tokens) <= max_tokens:
      return text

    truncated_tokens = (
      tokens[-max_tokens:] if keep_tail else tokens[:max_tokens]
    )
    return _encoding.decode(truncated_tokens)
  except Exception:
    return text
