from sqlmodel import Session, select
from app.model.bulk_import import BulkImport


def save_bulk_import(session: Session, bulk_import: BulkImport):
    session.add(bulk_import)
    session.flush()      # instead of commit()
    session.refresh(bulk_import)
    return bulk_import


def get_import_history(session: Session, skip: int = 0, limit: int = 20):
    return session.exec(
        select(BulkImport)
        .order_by(BulkImport.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()


def search_import_history(session: Session, query: str):
    return session.exec(
        select(BulkImport)
        .where(BulkImport.file_name.contains(query))
        .order_by(BulkImport.created_at.desc())
    ).all()