import random
import re
import string
import unicodedata


ASCII_LETTERS = string.ascii_letters + string.digits
ASCII_LETTERS_LIST = [c for c in ASCII_LETTERS]


def generate_random_letters(length):
  return ''.join(random.choices(ASCII_LETTERS_LIST, k=length))


def normalize_whitespaces(text):
  return re.sub(r'\s+', ' ', text).strip()


def normalize(text, to_lower=False):
  text = unicodedata.normalize('NFKC', text)
  text = normalize_whitespaces(text)
  return text.lower() if to_lower else text
