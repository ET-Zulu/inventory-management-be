from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class Vendor(SQLModel, table=True):
    __tablename__ = "vendors"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str

    contact_person: str = Field(default="")
    contact_info: str = Field(default="")
    location: str = Field(default="")

    lead_time: int = 0

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    deleted_at: datetime | None = None

    items: List["Item"] = Relationship(
        back_populates="vendor"
    )
