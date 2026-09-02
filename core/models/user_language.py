from django.db import models

from core.models.base import BaseModel


class UserLanguage(BaseModel):
  _soft_delete_parent_paths = ('user',)

  user = models.ForeignKey('User', on_delete=models.CASCADE)
  language_code = models.CharField(max_length=32)
  proficiency_uid = models.IntegerField()
  display_order = models.IntegerField(blank=True, default=0)

  class Meta(BaseModel.Meta):
    db_table = 'user_languages'
    constraints = [
      models.UniqueConstraint(
        fields=['user_id', 'language_code'],
        name='unique_user_language',
      ),
    ]

  def __str__(self) -> str:
    return (
      f'({self.id})user_id={self.user_id}:code={self.language_code}, '
      f'proficiency={self.proficiency_uid}'
    )
