from typing import TypedDict

from core.constants.language import LANGUAGE_PROFICIENCIES
from core.dtos.user.language import CreateUserLanguageDTO
from core.exceptions import DomainValidationError
from core.models import UserLanguage


class UserLanguageItem(TypedDict):
  id: int
  user_id: int
  language_code: str
  proficiency_uid: int
  display_order: int


def get_user_languages(
  user_id: int,
) -> list[UserLanguageItem]:
  return list(
    UserLanguage.objects
      .filter(user_id=user_id)
      .order_by('display_order', 'id')
      .values(
        'id',
        'user_id',
        'language_code',
        'proficiency_uid',
        'display_order',
      )
  )


def create_user_language(dto: CreateUserLanguageDTO) -> UserLanguage:
  count = UserLanguage.objects.filter(user_id=dto.user_id).count()
  if count >= LANGUAGE_PROFICIENCIES.get_max_languages():
    raise DomainValidationError(
      'Reached maximum language records per user.'
    )

  obj = UserLanguage(
    user_id=dto.user_id,
    language_code=dto.language_code,
    proficiency_uid=dto.proficiency_uid,
    display_order=dto.display_order,
  )
  obj.save()
  return obj
