from django.db import models
from django.db.models import Q

from core.models.base import BaseModel
from core.models.choices import DefaultJobState
from core.models.mixins.job import DefaultJobMixin


class EmailJob(BaseModel, DefaultJobMixin):
  _soft_delete_parent_paths = ('tenant', 'sender_user',)

  class EmailType(models.TextChoices):
    # User
    SIGNUP_WELCOME = 'user.signup_welcome', 'Signup welcome'
    EMAIL_VERIFICATION = 'user.email_verification', 'Email verification'
    PASSWORD_RESET = 'user.password_reset', 'Password reset'

    # Tenant
    TENANT_INVITE = 'tenant.invite', 'Tenant invite'

  tenant = models.ForeignKey(
    'Tenant',
    null=True,
    blank=True,
    on_delete=models.CASCADE,
  )
  sender_user = models.ForeignKey(
    'User',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
  )
  email_type = models.CharField(
    max_length=64,
    choices=EmailType.choices,
  )
  to_email = models.EmailField()
  template_vars = models.JSONField(default=dict)
  dedupe_key = models.CharField(max_length=255)
  last_task_id = models.CharField(max_length=255, null=True, blank=True)

  class Meta(BaseModel.Meta):
    db_table = 'email_jobs'
    constraints = [
      models.UniqueConstraint(
        fields=['dedupe_key'],
        condition=Q(state__in=[
          DefaultJobState.PENDING,
          DefaultJobState.RUNNING,
        ]),
        name='unique_email_job_active_dedupe_key',
      ),
    ]

  def __str__(self) -> str:
    return f'({self.id}){self.to_email}, {self.email_type}'



