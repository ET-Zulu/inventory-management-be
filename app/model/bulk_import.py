from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import ImportStatus


class BulkImport(SQLModel, table=True):
    __tablename__ = "bulk_imports"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    file_name: str

    records_processed: int = 0

    status: ImportStatus

    uploaded_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    uploader: Optional["User"] = Relationship(
        back_populates="bulk_imports"
    )
