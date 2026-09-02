from django.db import models

from core.constants import USER_EULA_VERSION
from core.models.base import BaseModel


class UserEulaAgreement(BaseModel):
  _soft_delete_parent_paths = ('user',)

  user = models.OneToOneField('User', on_delete=models.CASCADE)
  eula_version = models.CharField(
    max_length=64,
    blank=True,
    default=USER_EULA_VERSION,
  )
  agreed_at = models.DateTimeField(auto_now_add=True)

  class Meta(BaseModel.Meta):
    db_table = 'user_eula_agreements'

  def __str__(self) -> str:
    return f'({self.id})user_id={self.user_id}:{self.eula_version}'
