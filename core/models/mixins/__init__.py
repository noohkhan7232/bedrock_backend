from django.db import models
from django.utils import timezone


class SoftDeleteMixin(models.Model):
  deleted_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    abstract = True

  def delete(self, using=None, keep_parents=False):
    if self.deleted_at is not None:
      return

    self.deleted_at = timezone.now()
    self.save(update_fields=['deleted_at'])
