from django.db import models

from core.models.base import BaseModel


class EmailChange(BaseModel):
  _soft_delete_parent_paths = ('user',)

  user = models.ForeignKey('User', on_delete=models.CASCADE)
  new_email = models.EmailField(max_length=255)
  verification_code = models.CharField(max_length=255, unique=True)
  valid_until = models.DateTimeField()

  class Meta(BaseModel.Meta):
    db_table = 'email_changes'

  def __str__(self) -> str:
    return f'({self.id})new_email={self.new_email}'
