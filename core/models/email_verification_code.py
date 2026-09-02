import datetime
from django.conf import settings
from django.db import models

from core.models.base import BaseModel
from core.utils.clock import get_utc_now
from core.utils.text import generate_random_letters


class EmailVerificationCode(BaseModel):
  email = models.EmailField(max_length=255)
  verification_code = models.CharField(
    max_length=settings.EMAIL_VERIFICATION_CODE_LENGTH,
    unique=True,
  )
  valid_until = models.DateTimeField()

  class Meta(BaseModel.Meta):
    db_table = 'email_verification_codes'

  def set_verification_code(self):
    self.verification_code = generate_random_letters(
      length=settings.EMAIL_VERIFICATION_CODE_LENGTH,
    )
    self.valid_until = get_utc_now() + datetime.timedelta(
      hours=settings.EMAIL_VERIFICATION_CODE_LIFETIME_HOURS,
    )

  def __str__(self) -> str:
    return f'({self.id})verification code for {self.email}'
