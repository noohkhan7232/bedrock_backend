import random
import uuid
from pathlib import Path

from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.db import transaction

from core.constants import CONSTANTS
from core.constants.language import LANGUAGE_PROFICIENCIES
from core.management.commands.constants.test_data import (
  AVATAR_OUTPUT_DIR,
  AVATAR_FORMAT,
)
from core.models import (
  User,
  UserEulaAgreement,
  UserLanguage,
  UserLink,
)
from core.services.test_data.user_seed import (
  USER_CATEGORIES,
  HEADLINES,
  LOCALES,
  LOCALE_TO_TIMEZONES,
  LOCALE_TO_LANGUAGES,
  USER_LINK_TEMPLATES,
  TIMEZONE_TO_LOCATIONS,
  FIRST_NAMES,
  LAST_NAMES,
)
from core.utils.email import ensure_valid_email


DEFAULT_EMAIL_DOMAIN = 'test.com'

ENCODED_DEFAULT_PASSWORD = make_password('testtest')

AVATARS_SIZE = {
  'female': 500, # How many female avatars in AVATAR_OUTPUT_DIR?
  'male': 500, # How many male avatars in AVATAR_OUTPUT_DIR?
}


def _get_name(first_name: str, last_name: str) -> str:
  return f'{first_name} {last_name}'


def _get_email_from_name(first_name: str, last_name: str, count: int) -> str:
  email = f'{first_name}.{last_name}{count:03d}@{DEFAULT_EMAIL_DOMAIN}'
  return ensure_valid_email(email)


def get_avatar_filename(category: str, index: int) -> str:
  return f'{category}_{index:03d}.{AVATAR_FORMAT}'


def get_avatar_path(category: str, index: int) -> Path:
  filename = get_avatar_filename(category=category, index=index)
  return Path(AVATAR_OUTPUT_DIR) / filename


def _copy_avatar_and_get_relative_path(rng: random.Random, category: str) -> str:
  index = rng.randint(1, AVATARS_SIZE[category])
  src_path = get_avatar_path(category=category, index=index)
  if not src_path.exists():
    raise FileNotFoundError(f'Avatar file not found: {src_path}')

  filename = f'{uuid.uuid4().hex}.{AVATAR_FORMAT}'
  field = User._meta.get_field('image')
  relative_path = field.generate_filename(User(), filename)

  with src_path.open('rb') as f:
    saved_path = default_storage.save(relative_path, f)

  return saved_path


def build_user_instance(
  rng: random.Random,
  names_count: dict[str, int],
) -> User:
  category = rng.choice(USER_CATEGORIES)
  first_name = rng.choice(FIRST_NAMES[category])
  last_name = rng.choice(LAST_NAMES)

  name = _get_name(first_name=first_name, last_name=last_name)
  count = names_count[name] + 1 if name in names_count else 1
  email = _get_email_from_name(
    first_name=first_name,
    last_name=last_name,
    count=count,
  )

  headline = rng.choice(HEADLINES)
  if rng.random() < 0.2:
    headline = ''

  locale = rng.choices(
    population=LOCALES['population'],
    weights=LOCALES['weights'],
    k=1,
  )[0]

  timezone_code = rng.choices(
    population=LOCALE_TO_TIMEZONES[locale]['population'],
    weights=LOCALE_TO_TIMEZONES[locale]['weights'],
    k=1,
  )[0]

  location = rng.choice(TIMEZONE_TO_LOCATIONS[timezone_code])
  if rng.random() < 0.2:
    location = ''

  disable_promotion = rng.random() < 0.2

  user = User(
    first_name=first_name,
    last_name=last_name,
    email=email,
    password=ENCODED_DEFAULT_PASSWORD,
    headline=headline,
    locale=locale,
    timezone_code=timezone_code,
    location=location,
    disable_promotion=disable_promotion,
  )

  image_path = _copy_avatar_and_get_relative_path(rng=rng, category=category)
  user.image.name = image_path

  return user


def create_test_user_eula_agreements(
  users: list[User],
  batch_size: int,
) -> list[UserEulaAgreement]:
  agreements = [
    UserEulaAgreement(
      user_id=user.id,
      eula_version=CONSTANTS.USER_EULA_VERSION,
    ) for user in users
  ]
  return UserEulaAgreement.objects.bulk_create(agreements, batch_size=batch_size)


def create_test_user_languages(
  rng: random.Random,
  users: list[User],
  batch_size: int,
) -> list[UserLanguage]:
  languages: list[UserLanguage] = []

  for user in users:
    primary_code = LOCALE_TO_LANGUAGES[user.locale]['primary_code']
    secondary_codes = LOCALE_TO_LANGUAGES[user.locale]['secondary_codes']

    max_languages = 1 + len(secondary_codes)
    languages_count = rng.randint(0, max_languages)
    if languages_count == 0:
      continue

    languages.append(UserLanguage(
      user_id=user.id,
      language_code=primary_code,
      proficiency_uid=LANGUAGE_PROFICIENCIES.NATIVE.uid,
      display_order=1,
    ))

    if languages_count == 1:
      continue

    secondary_codes = rng.sample(
      population=secondary_codes,
      k=languages_count - 1,
    )

    for display_order, secondary_code in enumerate(secondary_codes, start=2):
      proficiency_uid = rng.choice(LANGUAGE_PROFICIENCIES.get_uid_list())

      languages.append(UserLanguage(
        user_id=user.id,
        language_code=secondary_code,
        proficiency_uid=proficiency_uid,
        display_order=display_order,
      ))

  return UserLanguage.objects.bulk_create(languages, batch_size=batch_size)


def create_test_user_links(
  rng: random.Random,
  users: list[User],
  batch_size: int,
) -> list[UserLink]:
  links: list[UserLink] = []

  for user in users:
    links_count = rng.randint(0, len(USER_LINK_TEMPLATES))
    if links_count == 0:
      continue

    templates = rng.sample(population=USER_LINK_TEMPLATES, k=links_count)
    local = user.email.split('@', 1)[0]
    handle = local.replace('.', '-')

    for display_order, template in enumerate(templates, start=1):
      links.append(UserLink(
        user_id=user.id,
        name=template['name'],
        url=template['url'].format(handle=handle),
        display_order=display_order,
      ))

  return UserLink.objects.bulk_create(links, batch_size=batch_size)


def create_test_users(
  rng: random.Random,
  count: int,
  batch_size: int = 500,
) -> list[User]:
  names_count: dict[str, int] = dict()
  users: list[User] = []

  for _ in range(count):
    user = build_user_instance(rng=rng, names_count=names_count)
    name = _get_name(first_name=user.first_name, last_name=user.last_name)
    names_count[name] = names_count[name] + 1 if name in names_count else 1
    users.append(user)

  with transaction.atomic():
    users = User.objects.bulk_create(users, batch_size=batch_size)

    create_test_user_eula_agreements(users=users, batch_size=batch_size)
    create_test_user_languages(rng=rng, users=users, batch_size=batch_size)
    create_test_user_links(rng=rng, users=users, batch_size=batch_size)

  return users
