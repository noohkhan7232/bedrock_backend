import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def get_random_bool(prob: float) -> bool:
  return random.random() < prob

def get_random_int(low: int, high: int) -> int:
  return random.randint(low, high)

def random_sample(
  seq: Sequence[T],
  size: int,
  allow_duplicates: bool = False,
) -> list[T]:
  if allow_duplicates:
    return random.choices(seq, k=size)
  return random.sample(seq, k=size)
