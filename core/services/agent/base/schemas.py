from pydantic import BaseModel, ConfigDict


class BaseOutputSchema(BaseModel):
  model_config = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    validate_assignment=True,
  )
