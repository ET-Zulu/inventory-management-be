from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class BulkImportResponse(BaseModel):
    id: UUID
    file_name: str
    records_processed: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ImportError(BaseModel):
    row: int
    field: str
    message: str


class ImportResponse(BaseModel):
    status: str
    records: int

class ImportHistoryResponse(BaseModel):
    file_name: str
    date: datetime
    records: int
    status: str
    file_link: str | None = None