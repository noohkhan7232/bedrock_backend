import random
import string


def generate_random_letters(length):
  ascii_letters = string.ascii_letters + string.digits
  return ''.join(random.choices(ascii_letters, k=length))
