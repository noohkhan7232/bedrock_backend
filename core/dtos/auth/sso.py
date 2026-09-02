from pydantic import BaseModel, EmailStr, Field


class GetSsoAuthorizationUrlDTO(BaseModel):
  email: EmailStr
  invitation_code: str = Field(default='')
  verification_code: str = Field(default='')


class GetSsoEnabledDTO(BaseModel):
  email_domain: str = Field(min_length=1, max_length=255)
