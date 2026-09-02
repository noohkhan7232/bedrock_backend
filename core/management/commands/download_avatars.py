import httpx
import random
import sys
from pathlib import Path
from urllib.parse import urlencode

from core.management.commands.base import HybridCommand
from core.management.commands.constants.test_data import (
  AVATAR_OUTPUT_DIR,
  AVATAR_FORMAT,
)
from core.services.test_data.user import get_avatar_filename


class Command(HybridCommand):
  BASE_URL = f'https://api.dicebear.com/9.x/adventurer/{AVATAR_FORMAT}'

  SHORT_HAIRS = [f'short{i:02d}' for i in range(1, 20)]
  LONG_HAIRS = [f'long{i:02d}' for i in range(1, 27)]

  PRESET_BY_CATEGORY = {
    'male': {
      'hair_pool': SHORT_HAIRS,
      'hair_probability': 90,
      'birthmark_probability': 0.08,
      'blush_probability': 0.10,
      'freckles_probability': 0.12,
      'mustache_probability': 0.28,
      'earrings_probability': 0,
    },
    'female': {
      'hair_pool': LONG_HAIRS,
      'hair_probability': 100,
      'birthmark_probability': 0.08,
      'blush_probability': 0.22,
      'freckles_probability': 0.16,
      'mustache_probability': 0,
      'earrings_probability': 30,
    },
  }

  def add_arguments(self, parser):
    super().add_arguments(parser=parser)

    parser.add_argument(
      '--males',
      required=False,
      type=int,
      help='The number of male images',
    )
    parser.add_argument(
      '--females',
      required=False,
      type=int,
      help='The number of female images',
    )
    parser.add_argument(
      '--seed',
      required=False,
      type=int,
      help='Optional random seed for reproducible avatar generation.',
    )

  def select_features(self, rng: random.Random, category: str) -> list[str]:
    preset = self.PRESET_BY_CATEGORY[category]
    features: list[str] = []

    if rng.random() < preset['birthmark_probability']:
      features.append('birthmark')
    if rng.random() < preset['blush_probability']:
      features.append('blush')
    if rng.random() < preset['freckles_probability']:
      features.append('freckles')
    if rng.random() < preset['mustache_probability']:
      features.append('mustache')

    return features

  def build_avatar_url(
    self,
    avatar_seed: str,
    category: str,
    rng: random.Random,
  ) -> str:
    preset = self.PRESET_BY_CATEGORY[category]
    hair = rng.choice(preset['hair_pool'])

    params = {
      'seed': avatar_seed,
      'flip': 'false',
      'radius': '50',
      'backgroundType': 'gradientLinear',
      'hair': hair,
      'hairProbability': str(preset['hair_probability']),
      'earringsProbability': str(preset['earrings_probability']),
    }

    features = self.select_features(rng=rng, category=category)
    if features:
      params['features'] = ','.join(features)
      params['featuresProbability'] = '100'

    return f'{self.BASE_URL}?{urlencode(params)}'

  def download_avatars(
    self,
    count: int,
    category: str,
    base_seed: int | None,
  ) -> None:
    path = Path(AVATAR_OUTPUT_DIR)
    path.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
      for i in range(count):
        avatar_seed = (
          f'{category}-{base_seed}-{i}'
        )
        rng = random.Random(avatar_seed)

        url = self.build_avatar_url(
          avatar_seed=avatar_seed,
          category=category,
          rng=rng,
        )

        response = client.get(url)
        response.raise_for_status()

        filename = get_avatar_filename(category=category, index=i)
        file_path = path / filename
        file_path = path / f'{category}_{i+1:03d}.{AVATAR_FORMAT}'
        file_path.write_bytes(response.content)
        sys.stdout.write(f'Downloaded: {file_path}\n')

  def handle(self, *args, **options):
    self.validate_options()

    n_males = self.option_int(
      key='males',
      prompt='The number of male images: ',
      min_value=0,
      max_value=500,
    ) or 0
    n_females = self.option_int(
      key='females',
      prompt='The number of female images: ',
      min_value=0,
      max_value=500,
    ) or 0
    seed = self.option_int(
      key='seed',
      prompt='Random seed (integer, optional): ',
    ) or 0

    self.download_avatars(count=n_males, category='male', base_seed=seed)
    self.download_avatars(count=n_females, category='female', base_seed=seed)

    sys.stdout.write(
      f'Successfully downloaded {n_males} male avatar(s) and '
      f'{n_females} female avatar(s).\n'
    )
