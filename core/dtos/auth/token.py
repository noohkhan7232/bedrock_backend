from pydantic import BaseModel, EmailStr, Field


class GetTokenPairDTO(BaseModel):
  ip_address: str | None = None
  email: EmailStr
  password: str = Field(default='')
  sso_code: str = Field(default='')


class TokenPairDTO(BaseModel):
  access: str = Field(min_length=1)
  refresh: str = Field(min_length=1)
  access_expires_in: int
  refresh_expires_in: int


class RefreshTokenDTO(BaseModel):
  refresh: str = Field(min_length=1)


class RefreshTokenResultDTO(BaseModel):
  refresh: str = Field(min_length=1)
  access: str = Field(min_length=1)
  access_expires_in: int


class RevokeTokenDTO(BaseModel):
  refresh: str = Field(min_length=1)


class RevokeTokenResultDTO(BaseModel):
  message: str = Field(min_length=1)
