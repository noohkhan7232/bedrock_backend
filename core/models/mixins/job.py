from django.db import models
from django.utils import timezone

from core.models.choices import DefaultJobState


class DefaultJobMixin(models.Model):
  State = DefaultJobState

  state = models.CharField(
    max_length=64,
    choices=DefaultJobState.choices,
    null=False,
    blank=False,
    default=DefaultJobState.PENDING,
  )
  error = models.TextField(blank=True, default='')

  started_at = models.DateTimeField(null=True, blank=True)
  finished_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    abstract = True

  def update_state_to(
    self,
    state: DefaultJobState,
    error: str | None = None,
    reason: str | None = None,
  ):
    if state == DefaultJobState.PENNDING:
      self.pend()
    elif state == DefaultJobState.RUNNING:
      self.start()
    elif state == DefaultJobState.DONE:
      self.succeed()
    elif state == DefaultJobState.FAILED:
      self.fail(error=error)
    elif state == DefaultJobState.CANCELLED:
      self.cancel(reason=reason)

  def reset(self):
    self.state = DefaultJobState.PENDING
    self.started_at = None
    self.finished_at = None
    self.error = ''

  def pend(self):
    if self.state not in (
      DefaultJobState.PENDING,
      DefaultJobState.RUNNING,
    ):
      raise ValueError(f'Cannot pend job from state={self.state}')
    self.state = DefaultJobState.PENDING
    self.started_at = None

  def start(self):
    if self.state not in (DefaultJobState.PENDING,):
      raise ValueError(f'Cannot start job from state={self.state}')
    self.state = DefaultJobState.RUNNING
    self.started_at = timezone.now()

  def succeed(self):
    if self.state not in (DefaultJobState.RUNNING,):
      raise ValueError(f'Cannot succeed from state={self.state}')
    self.state = DefaultJobState.DONE
    self.finished_at = timezone.now()
    self.error = ''

  def fail(self, error: str | None = None):
    if self.state not in (
      DefaultJobState.RUNNING,
      DefaultJobState.PENDING,
    ):
      raise ValueError(f'Cannot fail from state={self.state}')
    self.state = DefaultJobState.FAILED
    self.finished_at = timezone.now()
    self.error = (error or '')[:4000]

  def cancel(self, reason: str | None = None):
    if self.state in (
      DefaultJobState.DONE,
      DefaultJobState.FAILED,
      DefaultJobState.CANCELLED,
    ):
      return
    self.state = DefaultJobState.CANCELLED
    self.finished_at = timezone.now()
    if reason:
      self.error = (reason or '')[:4000]
