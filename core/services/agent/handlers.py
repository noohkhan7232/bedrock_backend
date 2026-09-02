import importlib
from typing import Protocol

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever

from core.dtos.agent import EnqueueAgentJobDTO


_HANDLER_KEY_MAP = {
  'assistant': 'core.services.agent.assistant:assistant'
}


class AgentHandler(Protocol):
  def __call__(
    self,
    dto: EnqueueAgentJobDTO,
    retriever: VectorStoreRetriever,
    llm_instant: BaseChatModel,
    llm_fast: BaseChatModel,
    llm_standard: BaseChatModel,
    callbacks: list = ...,
  ) -> str: ...


def resolve_handler(handler_key: str) -> AgentHandler:
  if handler_key not in _HANDLER_KEY_MAP:
    raise ValueError(f'Unknown handler_key: {handler_key}')

  try:
    handler_path = _HANDLER_KEY_MAP[handler_key]
    module_path, handler_name = handler_path.split(':', 1)
    module = importlib.import_module(module_path)
    handler = getattr(module, handler_name)
  except AttributeError:
    raise ValueError(f'Handler not found: {handler_path}')
  except Exception as e:
    raise ValueError(f'Failed to resolve handler: {handler_key}\n{e}')

  if not callable(handler):
    raise ValueError(f'Resolved handler is not callable: {handler_path}')

  return handler
