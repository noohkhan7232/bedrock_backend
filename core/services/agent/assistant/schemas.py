from enum import Enum
from typing import Optional
from pydantic import Field

from core.services.agent.base.schemas import BaseOutputSchema


class RouterAction(str, Enum):
  DOMAIN_INQUIRY = 'domain_inquiry'
  SUPPORT_ESCALATION = 'support_escalation'
  SUPPORT_INQUIRY = 'support_inquiry'
  SALES_INQUIRY = 'sales_inquiry'
  GENERAL_CHAT = 'general_chat'
  OFF_TOPIC = 'off_topic'


class RouterOutputSchema(BaseOutputSchema):
  action: RouterAction = Field(
    description='Decision for the incoming user input',
  )
  reasoning: str = Field(
    description='Brief reason for the classification. Useful for debugging.',
  )


class TriageAction(str, Enum):
  BLOCK = 'block'
  SUPPORT_ESCALATION = 'support_escalation'
  SUPPORT_INQUIRY = 'support_inquiry'
  CONTACT_SALES = 'contact_sales'
  GENERAL_CONVERSATION = 'general_conversation'
  TASK_QUERY = 'task_query'


class AssistantAction(str, Enum):
  BLOCK = 'block'
  KNOWLEDGE_QUERY = 'knowledge_query'
  WORKFLOW_GUIDANCE = 'workflow_guidance'
  DOMAIN_ADVISORY_QUERY = 'domain_advisory_query'


class TriageOutputSchema(BaseOutputSchema):
  content: Optional[str] = Field(default=None)
  action: TriageAction = (
    Field(description='Decision for the incoming user input')
  )


class TranslateOutputSchema(BaseOutputSchema):
  content: str = Field(min_length=1, description='Translated content')


class RephraseOutputSchema(BaseOutputSchema):
  content: str = Field(min_length=1, description='Rephrased user input')


class AssistantOutputSchema(BaseOutputSchema):
  content: str = Field(min_length=1, description='Rephrased user input')
  action: AssistantAction = (
    Field(description='Decision for the incoming user input')
  )
