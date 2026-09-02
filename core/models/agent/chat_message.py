from django.db import models

from core.models.base import BaseModel


class AgentChatMessage(BaseModel):
  class Sender(models.TextChoices):
    HUMAN = 'human', 'Human'
    AI = 'ai', 'AI'
    SYSTEM = 'system', 'System'

  agent_chat = models.ForeignKey(
    'AgentChat',
    on_delete=models.CASCADE,
    related_name='messages',
  )
  sender = models.CharField(max_length=64, choices=Sender.choices)
  content = models.TextField(blank=True)

  class Meta(BaseModel.Meta):
    db_table = 'agent_chat_messages'
    ordering = ['created_at']

  def __str__(self) -> str:
    return (
      f'({self.id})agent_chat_id={self.agent_chat_id}: {self.sender}'
    )

