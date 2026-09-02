from pydantic import BaseModel, ConfigDict

from core.models import AgentChat
from core.dtos.base import Id, UUId


class CreateAgentChatDTO(BaseModel):
  user_id: int
  tenant_id: int | None
  agent_type: AgentChat.AgentType


class EnqueueAgentJobDTO(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  agent_chat_id: UUId
  agent_chat_message_id: Id | None = None
  content: str
  tenant_id: Id | None
  user_id: Id
