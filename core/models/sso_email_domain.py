from django.db import models

from core.models.base import BaseModel


class SSOEmailDomain(BaseModel):
  domain = models.CharField(max_length=255, unique=True)
  connection_id = models.CharField(max_length=255)

  class Meta(BaseModel.Meta):
    db_table = 'sso_email_domains'

  def __str__(self) -> str:
    return f'({self.id})domain={self.domain}'
