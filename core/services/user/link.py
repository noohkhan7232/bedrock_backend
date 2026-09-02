from typing import TypedDict

from core.constants import CONSTANTS
from core.dtos.user.link import CreateUserLinkDTO
from core.exceptions import DomainValidationError
from core.models import UserLink


class UserLinkItem(TypedDict):
  id: int
  user_id: int
  name: str
  url: str
  display_order: int


def get_user_links(user_id: int) -> list[UserLinkItem]:
  return list(
    UserLink.objects
      .filter(user_id=user_id)
      .order_by('display_order', 'id')
      .values(
        'id',
        'user_id',
        'name',
        'url',
        'display_order',
      )
  )


def create_user_link(dto: CreateUserLinkDTO) -> UserLink:
  count = UserLink.objects.filter(user_id=dto.user_id).count()
  if count >= CONSTANTS.USER_LINKS_LIMIT:
    raise DomainValidationError(
      f'Reached max {CONSTANTS.USER_LINKS_LIMIT} links.'
    )

  obj = UserLink(
    user_id=dto.user_id,
    name=dto.name,
    url=dto.url,
    display_order=dto.display_order,
  )
  obj.save()
  return obj
