from django.db import models


class DefaultJobState(models.TextChoices):
  PENDING = 'pending', 'Pending'
  RUNNING = 'running', 'Running'
  DONE = 'done', 'Done'
  FAILED = 'failed', 'Failed'
  CANCELLED = 'cancelled', 'Cancelled'


class TenantLimitKey(models.TextChoices):
  TENANT_USERS_MAX = 'tenant_users_max', 'Tenant Users Max'
