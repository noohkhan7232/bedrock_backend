from django.db import models

from core.models.base import BaseModel


class UserLink(BaseModel):
  _soft_delete_parent_paths = ('user',)

  user = models.ForeignKey('User', on_delete=models.CASCADE)
  name = models.CharField(max_length=1024)
  url = models.CharField(max_length=1024)
  display_order = models.IntegerField(blank=True, default=0)

  class Meta(BaseModel.Meta):
    db_table = 'user_links'

  def __str__(self) -> str:
    return f'({self.id})user_id={self.user_id}:url={self.url}'
