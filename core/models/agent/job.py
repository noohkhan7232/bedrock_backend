import uuid
from django.db import models

from core.models.base import BaseModel
from core.models.mixins.job import DefaultJobMixin


class AgentJob(BaseModel, DefaultJobMixin):
  id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
  )
  agent_chat_message = models.OneToOneField(
    'AgentChatMessage',
    on_delete=models.CASCADE,
    related_name='jobs',
  )
  last_task_id = models.CharField(max_length=255, null=True, blank=True)

  class Meta(BaseModel.Meta):
    db_table = 'agent_jobs'

  def __str__(self) -> str:
    return (
      f'({self.id})agent_chat_message_id={self.agent_chat_message_id}'
    )
