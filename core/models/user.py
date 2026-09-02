from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.models.base import BaseModel
from core.models.managers import UserManager
from core.models.mixins import SoftDeleteMixin


class User(SoftDeleteMixin, AbstractUser, BaseModel):
  objects = UserManager()

  username = None
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name', 'last_name',]

  email = models.EmailField(max_length=255, db_index=True)
  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255)
  image = models.ImageField(
    verbose_name='user image',
    null=True,
    blank=True,
    upload_to='images/users/%Y/%m/',
  )
  status = models.IntegerField(default=0)
  headline = models.CharField(max_length=255, blank=True, default='')
  location = models.CharField(max_length=255, blank=True, default='')
  locale = models.CharField(max_length=32, default='en')
  timezone_code = models.CharField(
    max_length=64,
    default='America/Los_Angeles',
  )
  disable_promotion = models.BooleanField(default=False)

  class Meta(BaseModel.Meta):
    db_table = 'users'
    constraints = [
      models.UniqueConstraint(
        fields=['email'],
        name='unique_user_normalized_email',
        condition=Q(deleted_at__isnull=True),
      ),
    ]

  def delete(self, using=None, keep_parents=False):
    if not self.deleted_at:
      self.deleted_at = timezone.now()
      self.save(update_fields=['deleted_at'])
      self.tenantuser_set.update(deleted_at=self.deleted_at)

  def __str__(self) -> str:
    return (
      f'({self.id}){self.email}:{self.first_name} {self.last_name}'
    )
