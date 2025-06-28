from pydantic import BaseModel


class ChatResponseEvent(BaseModel):
    session_id: str
    prompt: str
