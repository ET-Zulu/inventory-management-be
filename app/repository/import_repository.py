from sqlmodel import Session
from app.model.bulk_import import BulkImport


def save_bulk_import(session: Session, bulk_import: BulkImport):
    session.add(bulk_import)
    session.commit()
    session.refresh(bulk_import)
    return bulk_import