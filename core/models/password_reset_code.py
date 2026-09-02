import datetime

from django.conf import settings
from django.db import models

from core.models.base import BaseModel
from core.utils.clock import get_utc_now
from core.utils.text import generate_random_letters


class PasswordResetCode(BaseModel):
  email = models.EmailField(max_length=255)
  reset_code = models.CharField(
    max_length=settings.PASSWORD_RESET_CODE_LENGTH,
    unique=True,
  )
  valid_until = models.DateTimeField()

  class Meta(BaseModel.Meta):
    db_table = 'password_reset_codes'

  def set_reset_code(self):
    self.reset_code = generate_random_letters(
      length=settings.PASSWORD_RESET_CODE_LENGTH,
    )
    self.valid_until = get_utc_now() + datetime.timedelta(
      hours=settings.PASSWORD_RESET_CODE_LIFETIME_HOURS,
    )

  def __str__(self) -> str:
    return f'({self.id})reset code for {self.email}'
