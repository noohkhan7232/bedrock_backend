from enum import Enum
from typing import Any


class LLMType(Enum):
  INSTANT = 'instant'
  FAST = 'fast'
  STANDARD = 'standard'
  REASONING = 'reasoning'


LLM_CONFIG = {
  'instant': {
    'provider': 'openai',
    'params': {
      'model': 'gpt-5-nano',
      #'temperature': 0.3,
      #'top_p': 1.0,
      'max_tokens': 1024,
      'timeout': 20.0,
      'max_retries': 2,
      'seed': 0,
    },
  },
  'fast': {
    'provider': 'openai',
    'params': {
      'model': 'gpt-5-mini',
      #'temperature': 0.3,
      #'top_p': 0.9,
      'max_tokens': 2048,
      'timeout': 30.0,
      'max_retries': 2,
      'seed': 0,
    }
  },
  'standard': {
    'provider': 'openai',
    'params': {
      'model': 'gpt-5.2',
      'temperature': 0,
      'top_p': 0.9,
      'max_tokens': 4096,
      'timeout': 60.0,
      'max_retries': 2,
      'seed': 0,
    },
  },
  'reasoning': {
    'provider': 'openai',
    'params': {
      'model': 'gpt-5.2',
      'temperature': 0,
      'top_p': 1.0,
      'max_tokens': 4096,
      'timeout': 180.0,
      'max_retries': 2,
      'seed': 0,
      'reasoning_effort': 'medium',
    },
  },
}


def get_llm_class(provider):
  from langchain_openai import ChatOpenAI
  if provider == 'openai':
    return ChatOpenAI

  raise ValueError(f'Provider {provider} is not supported.')


def create_llm(llm_type, streaming=True, **kwargs) -> Any:
  if llm_type not in LLM_CONFIG:
    raise ValueError('Invalid llm_type: {llm_type}')
  config = LLM_CONFIG[llm_type]

  provider = config.get('provider', 'openai')
  params =config['params']
  llm_class = get_llm_class(provider=provider)

  return llm_class(
    streaming=streaming,
    **params,
    **kwargs,
  )
