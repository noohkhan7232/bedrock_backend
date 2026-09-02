from pydantic import BaseModel


class CreateUserLanguageDTO(BaseModel):
  user_id: int
  language_code: str
  proficiency_uid: int
  display_order: int
