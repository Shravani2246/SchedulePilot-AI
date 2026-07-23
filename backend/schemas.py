from pydantic import BaseModel


class ChatRequest(BaseModel):

    question: str

    namespace: str

    thread_id: str