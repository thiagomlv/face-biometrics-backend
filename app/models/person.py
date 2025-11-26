from typing import Annotated
from pydantic import BaseModel, conlist

class Person(BaseModel):
    id: int | None = None
    name: str
    facial_vector: Annotated[
        list[float],
        conlist(item_type=float, min_length=128, max_length=128)
    ] | None = None
    photo_url: str | None = None
    email: str
    room_id: int | None = None
    user_id: int | None = None
