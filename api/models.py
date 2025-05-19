from pydantic import BaseModel
from typing import Optional

class BookingRequest(BaseModel):
    name: str
    email: str
    date: str
    time: str
    title: str
    description: Optional[str] = None