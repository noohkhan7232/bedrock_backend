import uuid
from typing import Annotated
from pydantic import BaseModel, PositiveInt, StringConstraints


Id = PositiveInt
UUId = uuid.UUID

Name = Annotated[
  str,
  StringConstraints(
    strip_whitespace=True,
    min_length=1,
    max_length=200,
  ),
]

class BaseDTO(BaseModel):
  model_config = dict(from_attributes=True)
