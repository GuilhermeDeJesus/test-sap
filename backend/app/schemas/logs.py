from pydantic import BaseModel


class LogFileResponse(BaseModel):
    name: str
    size: int


class PresignedResponse(BaseModel):
    url: str
