import uuid
from django.db import models

from core.models.base import BaseModel


class AgentChat(BaseModel):
  _soft_delete_parent_paths = ('user', 'tenant',)

  class AgentType(models.TextChoices):
    ASSISTANT = 'assistant', 'Assistant'

  id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
  )
  user = models.ForeignKey('User', on_delete=models.CASCADE)
  tenant = models.ForeignKey(
    'Tenant',
    null=True,
    blank=True,
    on_delete=models.CASCADE,
  )
  agent_type = models.CharField(
    max_length=64,
    choices=AgentType.choices,
  )

  class Meta(BaseModel.Meta):
    db_table = 'agent_chats'

  def __str__(self) -> str:
    return f'({self.id}){self.agent_type}, user_id={self.user_id}'
