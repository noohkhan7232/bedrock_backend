from pydantic import BaseModel


class CreateUserLinkDTO(BaseModel):
  user_id: int
  name: str
  url: str
  display_order: int
