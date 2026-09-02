from django.db import models

from core.models.base import BaseModel


class FailedLoginAttempt(BaseModel):
  ip_address = models.CharField(max_length=64, blank=True, default='')
  email = models.EmailField(max_length=255)
  attempted_at = models.DateTimeField(auto_now_add=True)

  class Meta(BaseModel.Meta):
    db_table = 'failed_login_attempts'

  def __str__(self) -> str:
    return f'({self.id}){self.email} from {self.ip_address}'
