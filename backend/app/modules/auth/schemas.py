from pydantic import BaseModel


class GoogleAuthRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    default_llm_provider: str = "openai"

    model_config = {"from_attributes": True}
