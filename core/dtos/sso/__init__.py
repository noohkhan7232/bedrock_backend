from pydantic import BaseModel, Field


class CreateSSOEmailDomainDTO(BaseModel):
  domain: str = Field(min_length=3, max_length=255)
  connection_id: str = Field(min_length=1, max_length=255)
