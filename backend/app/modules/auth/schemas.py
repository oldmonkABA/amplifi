from uuid import UUID

from pydantic import BaseModel, field_serializer


class GoogleAuthRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    default_llm_provider: str = "openai"

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)
