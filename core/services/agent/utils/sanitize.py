import re
import unicodedata


_CTRL_RE = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\x80-\x9F]')
_ANSI_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
_FORMAT_RE = re.compile(
  r'['
  '\u00AD'
  '\u0600-\u0605'
  '\u061C'
  '\u06DD'
  '\u070F'
  '\u08E2'
  '\u180E'
  '\u200B-\u200F'  # Includes \u200b
  '\u202A-\u202E'
  '\u2060-\u2064'
  '\u2066-\u2069'
  '\u206A-\u206F'
  '\uFEFF'         # Zero Width No-Break Space (BOM)
  '\uFFF9-\uFFFB'
  '\U000110BD'
  '\U000110CD'
  '\U00013430-\U00013438'
  '\U000E0001'
  '\U000E0020-\U000E007F'
  ']'
)
_WHITESPACE_RE = re.compile(r'\s+')


def normalize_unicode(text: str) -> str:
  return unicodedata.normalize('NFKC', text)


def sanitize_chars(text: str) -> str:
  text = _CTRL_RE.sub('', text)
  text = _ANSI_RE.sub('', text)
  text = _FORMAT_RE.sub('', text)
  text = _WHITESPACE_RE.sub(' ', text).strip()
  return text


def limit_repetitions(text: str, max_run: int=5) -> str:
  pattern = re.compile(r'(.)\1{%d,}' % (max_run - 1))
  return pattern.sub(r'\1' * max_run, text)


def break_code_fences(text: str) -> str:
  return text.replace('```', '`\u200b`\u200b`')


def truncate(text: str, max_len: int=30_000):
  return (
    text[:max_len] + '\n[...truncated for safety...]'
    if len(text) > max_len else text
  )


def normalize_markdown(md: str) -> str:
  md = re.sub(r'\n{3,}', '\n\n', md)
  md = re.sub(r'[ \t]+$', '', md, flags=re.MULTILINE)
  return md.strip()


def sanitize_user_query(
  text: str,
  max_len: int = 30_000,
) -> str:
  text = normalize_unicode(text)
  text = sanitize_chars(text)
  text = limit_repetitions(text)
  text = break_code_fences(text)
  text = truncate(text, max_len=max_len)
  return text


def sanitize_prompt(
  text: str,
) -> str:
  text = normalize_unicode(text)
  text = normalize_markdown(md=text)
  text = sanitize_chars(text)
  text = limit_repetitions(text)
  return text


def sanitize_knowledge_base(
  text: str,
) -> str:
  text = normalize_markdown(md=text)
  text = sanitize_chars(text)
  text = limit_repetitions(text)
  return text
