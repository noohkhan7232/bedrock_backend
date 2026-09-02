from typing import List, Any

from django.db import transaction
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from core.models import AgentChatMessage
from core.services.agent.utils.strings import (
  count_tokens,
  truncate_text_by_tokens,
)


def get_chat_messages(
  agent_chat_id: str,
  limit: int = 4,
  max_tokens: int | None = None,
  include_system_messages: bool = False,
  allow_truncate_in_message: bool = True,
) -> List[Any]:
  query = (
    AgentChatMessage.objects
      .filter(
        agent_chat_id=agent_chat_id,
        agent_chat__tenant__deleted_at__isnull=True,
      )
      .order_by('-created_at')[:limit]
  )

  chat_messages = []
  for obj in list(query.all()):
    if obj.sender == AgentChatMessage.Sender.HUMAN:
      chat_messages.append(HumanMessage(content=obj.content))
    elif obj.sender == AgentChatMessage.Sender.AI:
      chat_messages.append(AIMessage(content=obj.content))
    elif include_system_messages:
      chat_messages.append(SystemMessage(content=obj.content))

  if max_tokens is None:
    return chat_messages

  truncated_chat_messages = []
  total_tokens_count = 0
  for msg in list(reversed(chat_messages)):
    tokens_count = count_tokens(msg.content)

    if total_tokens_count + tokens_count <= max_tokens:
      truncated_chat_messages.append(msg)
      total_tokens_count += tokens_count
      continue

    if not allow_truncate_in_message:
      break

    if not truncated_chat_messages and tokens_count > 0:
      truncated_content = truncate_text_by_tokens(
        text=msg.content,
        max_tokens=max_tokens,
        keep_tail=True,
      )
      truncated_chat_messages.append(type(msg)(content=truncated_content))

  return list(reversed(truncated_chat_messages))


def create_chat_message(
  agent_chat_id: str,
  sender: AgentChatMessage.Sender,
  content: str,
) -> AgentChatMessage:
  return AgentChatMessage.objects.create(
    agent_chat_id=agent_chat_id,
    sender=sender,
    content=content,
  )


def create_human_chat_message(
  agent_chat_id: str,
  content: str,
) -> AgentChatMessage:
  return create_chat_message(
    agent_chat_id=agent_chat_id,
    sender=AgentChatMessage.Sender.HUMAN,
    content=content,
  )


def create_ai_chat_message(
  agent_chat_id: str,
  content: str,
) -> AgentChatMessage:
  return create_chat_message(
    agent_chat_id=agent_chat_id,
    sender=AgentChatMessage.Sender.AI,
    content=content,
  )


def delete_subsequent_chat_messages(
  user_id: int,
  agent_chat_id: str,
  agent_chat_message_id: int,
) -> None:
  obj = AgentChatMessage.objects.get(
    id=agent_chat_message_id,
    agent_chat_id=agent_chat_id,
    agent_chat__user__id=user_id,
    agent_chat__user__deleted_at__isnull=True,
  )
  AgentChatMessage.objects.filter(
    agent_chat_id=agent_chat_id,
    agent_chat__user__id=user_id,
    agent_chat__user__deleted_at__isnull=True,
    created_at__gt=obj.created_at
  ).all().delete()


def update_human_chat_message(
  user_id: int,
  content: str,
  agent_chat_id: str,
  agent_chat_message_id: int,
) -> AgentChatMessage:
  with transaction.atomic():
    human_chat_message = (
      AgentChatMessage.objects
        .select_for_update(of=('self',))
        .get(
          id=agent_chat_message_id,
          agent_chat_id=agent_chat_id,
          agent_chat__user__id=user_id,
          agent_chat__user__deleted_at__isnull=True,
          sender=AgentChatMessage.Sender.HUMAN,
        )
    )
    human_chat_message.content = content
    human_chat_message.save(update_fields=['content'])

    delete_subsequent_chat_messages(
      user_id=user_id,
      agent_chat_id=agent_chat_id,
      agent_chat_message_id=agent_chat_message_id,
    )

    return human_chat_message
