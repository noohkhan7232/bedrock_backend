from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import VectorStoreRetriever

from core.dtos.agent import EnqueueAgentJobDTO
from core.services.agent.utils.chat_message import get_chat_messages
from core.services.agent.utils.guardrails import is_blank_text, validate_input
from core.services.agent.utils.prompt import (
  serialize_user_profile_for_prompt,
  serialize_tenant_user_profile_for_prompt,
  get_user_prompt,
)
from core.services.agent.utils.resources import (
  fetch_user,
  fetch_tenant_user,
)
from core.services.agent.utils.responses import TEMPLATE_RESPONSES
from core.services.agent.utils.strings import detect_language_code
from .prompts import PROMPTS


def get_language(user_input: str, thresh=0.5) -> tuple[str, str]:
  lang_code, language, confidence = detect_language_code(text=user_input)
  if confidence < thresh:
    lang_code = 'en'
    language = 'English'
  return lang_code, language


def input_guardrails(user_input: str, lang_code='en'):
  resp = {
    'is_empty': False,
    'block': False,
    'reason': '',
    'content': '',
  }

  if is_blank_text(text=user_input):
    resp['is_empty'] = True
    resp['block'] = True
    resp['reason'] = 'Input is empty'
    resp['content'] = TEMPLATE_RESPONSES['empty_input']

  if not validate_input(user_input):
    resp['block'] = True
    resp['reason'] = 'Input violates policy.'
    resp['content'] = TEMPLATE_RESPONSES['block']

  return resp


def main_router(
  llm: BaseChatModel,
  user_input: str,
  chat_messages: list,
  callbacks: list = [],
):
  system_prompt = PROMPTS['router']
  user_prompt = get_user_prompt(use_profile=False, use_context=False)
  prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', user_prompt),
  ])

  chain = prompt | llm | StrOutputParser()
  action = chain.invoke(
    input={
    'input': user_input,
    'chat_history': chat_messages,
    },
    config={
      'callbacks': callbacks,
      'verbose': False,
    },
  )

  return action


def static_handler(action: str, lang_code: str = 'en'):
  # TODO: create template responses per action per lang_code
  if action in TEMPLATE_RESPONSES:
    return TEMPLATE_RESPONSES[action]
  return ''


def generate_general_chat_response(
  llm: BaseChatModel,
  user_input: str,
  chat_messages: list,
  language: str,
  callbacks: list,
):
  system_prompt = PROMPTS['general_chat']
  user_prompt = get_user_prompt(use_profile=False, use_context=False)
  prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', user_prompt),
  ])

  chain = prompt | llm | StrOutputParser()
  content = chain.invoke(
    input={
      'input': user_input,
      'chat_history': chat_messages,
      'language': language,
    },
    config={
      'callbacks': callbacks,
      'verbose': False,
    },
  )
  return content


def generate_off_topic_response(
  llm: BaseChatModel,
  user_input: str,
  chat_messages: list,
  language: str,
  callbacks: list,
):
  system_prompt = PROMPTS['off_topic']
  user_prompt = get_user_prompt(use_profile=False, use_context=False)
  prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', user_prompt),
  ])

  chain = prompt | llm | StrOutputParser()
  content = chain.invoke(
    input={
      'input': user_input,
      'chat_history': chat_messages,
      'language': language,
    },
    config={
      'callbacks': callbacks,
      'verbose': False,
    },
  )
  return content


def retrieve_relevant_documents(
  llm: BaseChatModel,
  retriever: VectorStoreRetriever,
  user_input: str,
  chat_messages: list,
  language: str,
  callbacks: list = [],
):
  system_prompt = PROMPTS['rephrase']
  user_prompt = get_user_prompt(use_profile=False, use_context=False)
  prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', user_prompt),
  ])

  chain = prompt | llm | StrOutputParser()
  rephrased_user_input = chain.invoke(
    input={
      'input': user_input,
      'chat_history': chat_messages,
      'language': language,
    },
    config={
      'callbacks': callbacks,
      'verbose': False,
    },
  )

  retrieved_docs = retriever.invoke(
    rephrased_user_input,
    config={
      'verbose': False,
    },
  )
  return retrieved_docs


def get_profile_json(
  user_id: int,
  tenant_id: int | None = None,
):
  user = fetch_user(user_id=user_id)
  tenant_user = fetch_tenant_user(user_id=user_id, tenant_id=tenant_id)
  profile_json = (
    serialize_tenant_user_profile_for_prompt(tenant_user=tenant_user)
    if tenant_user else serialize_user_profile_for_prompt(user=user)
  )
  return profile_json


def response_domain_inquiry(
  llm: BaseChatModel,
  user_input: str,
  chat_messages: list,
  context: list,
  profile_json: str,
  language: str,
  callbacks: list,
):
  system_prompt = PROMPTS['domain_inquiry']
  user_prompt = get_user_prompt(use_profile=True, use_context=True)

  prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', user_prompt),
  ])
  chain = prompt | llm | StrOutputParser()
  content = chain.invoke(
    input={
      'input': user_input,
      'chat_history': chat_messages,
      'context': context,
      'profile_json': profile_json,
      'language': language,
    },
    config={
      'callbacks': callbacks,
      'verbose': False,
    },
  )
  return content


def assistant(
  dto: EnqueueAgentJobDTO,
  retriever: VectorStoreRetriever,
  llm_instant: BaseChatModel,
  llm_fast: BaseChatModel,
  llm_standard: BaseChatModel,
  callbacks: list = [],
) -> str:
  user_input = dto.content
  content = TEMPLATE_RESPONSES['block']

  lang_code, language = get_language(user_input=user_input)
  result = input_guardrails(user_input=user_input, lang_code=lang_code)
  if result['content']:
    return result['content']

  chat_messages = get_chat_messages(
    agent_chat_id=dto.agent_chat_id, limit=6, max_tokens=2000)

  action = main_router(
    llm=llm_instant,
    user_input=user_input,
    chat_messages=chat_messages,
    callbacks=callbacks,
  )
  content = static_handler(action=action, lang_code=lang_code)
  if content:
    return content

  if action == 'general_chat':
    content = generate_general_chat_response(
      llm=llm_instant,
      user_input=user_input,
      chat_messages=chat_messages,
      language=language,
      callbacks=callbacks,
    )
    return content
  elif action == 'off_topic':
    content = generate_off_topic_response(
      llm=llm_instant,
      user_input=user_input,
      chat_messages=chat_messages,
      language=language,
      callbacks=callbacks,
    )
    return content

  context = retrieve_relevant_documents(
    llm=llm_instant,
    retriever=retriever,
    user_input=user_input,
    chat_messages=chat_messages,
    language=language,
    callbacks=callbacks,
  )

  profile_json = get_profile_json(user_id=dto.user_id, tenant_id=dto.tenant_id)
  chat_messages = get_chat_messages(
    agent_chat_id=dto.agent_chat_id, limit=10, max_tokens=6000)

  content = response_domain_inquiry(
    llm=llm_standard,
    user_input=user_input,
    chat_messages=chat_messages,
    context=context,
    profile_json=profile_json,
    language=language,
    callbacks=callbacks,
  )

  return content
