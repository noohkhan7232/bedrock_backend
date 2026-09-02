from django.conf import settings
from django.db import models

from core.models.base import BaseModel
from core.models.mixins import SoftDeleteMixin
from core.utils.text import generate_random_letters


class Tenant(SoftDeleteMixin, BaseModel):
  name = models.CharField(max_length=255)
  domain = models.CharField(
    max_length=settings.TENANT_DOMAIN_LENGTH,
    unique=True,
  )
  account_id = models.CharField(
    max_length=settings.TENANT_ACCOUNT_ID_LENGTH,
    unique=True,
  )
  image = models.ImageField(
    verbose_name='tenant logo image',
    null=True,
    blank=True,
    upload_to='images/tenants/%Y/%m/',
  )
  description = models.CharField(
    max_length=1024,
    blank=True,
    default='',
  )

  class Meta(BaseModel.Meta):
    db_table = 'tenants'

  @classmethod
  def get_id_from(cls, domain):
    return cls.objects.get(domain=domain).id

  def set_domain(self):
    self.domain = generate_random_letters(
      length=settings.TENANT_DOMAIN_LENGTH,
    )

  def set_account_id(self):
    self.account_id = generate_random_letters(
      length=settings.TENANT_ACCOUNT_ID_LENGTH,
    )

  def __str__(self) -> str:
    return f'({self.id}){self.name}, {self.domain[:8]}...'
