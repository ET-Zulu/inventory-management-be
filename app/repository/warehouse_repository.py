from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.model.item import Item
from app.model.warehouse import Warehouse


def get_warehouse_by_name(session: Session, name: str) -> Optional[Warehouse]:
    return session.exec(
        select(Warehouse).where(Warehouse.name == name)
    ).first()


def get_all_active_warehouses(session: Session) -> List[Warehouse]:
    return session.exec(
        select(Warehouse)
        .where(Warehouse.is_active == True)  # noqa: E712
        .order_by(Warehouse.created_at.desc())
    ).all()


def get_filtered_warehouses(session: Session, page: int, limit: int) -> Tuple[List[Warehouse], int]:
    query = select(Warehouse).where(Warehouse.is_active == True)  # noqa: E712
    count_query = select(func.count()).select_from(Warehouse).where(
        Warehouse.is_active == True  # noqa: E712
    )

    total = session.exec(count_query).one()
    offset = (page - 1) * limit
    warehouses = session.exec(
        query.order_by(Warehouse.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return warehouses, total or 0


def get_warehouse_by_id(session: Session, warehouse_id: UUID) -> Optional[Warehouse]:
    return session.exec(
        select(Warehouse).where(
            Warehouse.id == warehouse_id,
            Warehouse.is_active == True,  # noqa: E712
        )
    ).first()


def save_warehouse(session: Session, warehouse: Warehouse) -> Warehouse:
    session.add(warehouse)
    session.commit()
    session.refresh(warehouse)
    return warehouse


def count_used_capacity(session: Session, warehouse_id: UUID) -> int:
    """Sum of quantity_on_hand for all active items in this warehouse."""
    result = session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0)).where(
            Item.warehouse_id == warehouse_id,
            Item.is_active == True,  # noqa: E712
        )
    ).one()
    return int(result or 0)


def count_active_warehouses(session: Session) -> int:
    result = session.exec(
        select(func.count()).select_from(Warehouse).where(
            Warehouse.is_active == True  # noqa: E712
        )
    ).one()
    return result or 0
