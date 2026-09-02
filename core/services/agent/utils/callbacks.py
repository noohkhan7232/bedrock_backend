import time
from typing import Any, Callable, Dict, List

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage


class ThrottledCallbackHandler(BaseCallbackHandler):
  def __init__(
    self,
    interval,
    callback: Callable[..., bool],
    concatenate_text=False,
    disable_on_llm_new_token=False,
    disable_on_llm_start=False,
    disable_on_tool_start=False,
    **kwargs,
  ):
    self.interval = interval
    self.callback = callback
    self.concatenate_text = concatenate_text
    self.disable_on_llm_new_token = disable_on_llm_new_token
    self.disable_on_llm_start = disable_on_llm_start
    self.disable_on_tool_start = disable_on_tool_start
    self.kwargs = kwargs

    self.last_callback_time = time.time()
    self.disable_callback = False
    self.kwargs['current_text'] = ''

  def _throttled_callback(self):
    if self.disable_callback:
      return

    current_time = time.time()
    if current_time - self.last_callback_time < self.interval:
      return

    self.last_callback_time = current_time
    self.disable_callback = self.callback(**self.kwargs)

  def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
    if self.concatenate_text:
      self.kwargs['current_text'] += token
    if not self.disable_on_llm_new_token:
      self._throttled_callback()

  def on_llm_start(
    self,
    serialized: Dict[str, Any],
    prompts: List[str],
    **kwargs,
  ) -> None:
    if not self.disable_on_llm_start:
      self._throttled_callback()

  def on_chat_model_start(
    self,
    serialized: Dict[str, Any],
    messages: List[List[BaseMessage]],
    **kwargs: Any,
  ) -> None:
    if not self.disable_on_llm_start:
      self._throttled_callback()

  def on_tool_start(
    self,
    serializerd: Dict[str, Any],
    input_str: str,
    **kwargs: Any,
  ) -> None:
    if not self.disable_on_tool_start:
      self._throttled_callback()
