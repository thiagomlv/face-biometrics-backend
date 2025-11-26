from pydantic import BaseModel

class Room(BaseModel):
    id: int | None = None
    name: str
    location: str | None = None
    user_id: int | None = None
