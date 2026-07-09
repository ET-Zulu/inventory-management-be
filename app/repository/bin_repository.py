from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.model.bin import Bin
from app.model.item import Item


GENERAL_STORAGE_BIN_NAME = "General Storage"


def get_bin_by_id(session: Session, bin_id: UUID) -> Optional[Bin]:
    return session.exec(
        select(Bin).where(Bin.id == bin_id, Bin.deleted_at.is_(None))
    ).first()


def get_bin_by_name(session: Session, warehouse_id: UUID, name: str) -> Optional[Bin]:
    return session.exec(
        select(Bin).where(
            Bin.warehouse_id == warehouse_id,
            func.lower(Bin.name) == name.strip().lower(),
            Bin.deleted_at.is_(None),
        )
    ).first()


def get_general_storage_bin(session: Session, warehouse_id: UUID) -> Optional[Bin]:
    return session.exec(
        select(Bin).where(
            Bin.warehouse_id == warehouse_id,
            Bin.name == GENERAL_STORAGE_BIN_NAME,
            Bin.is_system == True,  # noqa: E712
            Bin.deleted_at.is_(None),
        )
    ).first()


def ensure_general_storage_bin(session: Session, warehouse_id: UUID) -> Bin:
    existing = get_general_storage_bin(session, warehouse_id)
    if existing:
        return existing

    bin_ = Bin(
        warehouse_id=warehouse_id,
        name=GENERAL_STORAGE_BIN_NAME,
        is_system=True,
    )
    session.add(bin_)
    session.commit()
    session.refresh(bin_)
    return bin_


def save_bin(session: Session, bin_: Bin) -> Bin:
    session.add(bin_)
    session.commit()
    session.refresh(bin_)
    return bin_


def get_filtered_bins(
    session: Session,
    warehouse_id: UUID,
    page: int,
    limit: int,
) -> Tuple[List[Bin], int]:
    query = (
        select(Bin)
        .where(Bin.warehouse_id == warehouse_id, Bin.deleted_at.is_(None))
        .order_by(Bin.is_system.desc(), Bin.created_at.desc())
    )
    count_query = (
        select(func.count())
        .select_from(Bin)
        .where(Bin.warehouse_id == warehouse_id, Bin.deleted_at.is_(None))
    )
    total = session.exec(count_query).one()
    offset = (page - 1) * limit
    bins = session.exec(query.offset(offset).limit(limit)).all()
    return bins, int(total or 0)


def count_items_in_bin(session: Session, bin_id: UUID) -> int:
    result = session.exec(
        select(func.count()).select_from(Item).where(
            Item.bin_id == bin_id
        )
    ).one()
    return int(result or 0)


def count_bins_in_warehouse(session: Session, warehouse_id: UUID) -> int:
    result = session.exec(
        select(func.count()).select_from(Bin).where(
            Bin.warehouse_id == warehouse_id,
            Bin.deleted_at.is_(None),
        )
    ).one()
    return int(result or 0)

