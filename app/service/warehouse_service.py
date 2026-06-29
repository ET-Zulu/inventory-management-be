from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.model.warehouse import Warehouse
from app.schemas.warehouse import WarehouseResponse
from app.repository import warehouse_repository


def _to_response(session: Session, warehouse: Warehouse) -> WarehouseResponse:
    used_capacity = warehouse_repository.count_used_capacity(session, warehouse.id)
    available_capacity = max(0, warehouse.capacity - used_capacity)
    return WarehouseResponse(
        id=warehouse.id,
        name=warehouse.name,
        location=warehouse.location,
        capacity=warehouse.capacity,
        description=warehouse.description,
        created_at=warehouse.created_at,
        used_capacity=used_capacity,
        available_capacity=available_capacity,
    )


def create_warehouse(session: Session, payload) -> Warehouse:
    existing = warehouse_repository.get_warehouse_by_name(session, payload.name)
    if existing:
        if existing.is_active:
            raise ValueError(f"Warehouse '{payload.name}' already exists")
        # Reactivate soft-deleted warehouse
        existing.is_active = True
        existing.deleted_at = None
        existing.location = payload.location
        existing.capacity = payload.capacity
        existing.description = payload.description
        return warehouse_repository.save_warehouse(session, existing)

    warehouse = Warehouse(
        name=payload.name,
        location=payload.location,
        capacity=payload.capacity,
        description=payload.description,
    )
    return warehouse_repository.save_warehouse(session, warehouse)


def get_all_warehouses(session: Session) -> List[WarehouseResponse]:
    warehouses = warehouse_repository.get_all_active_warehouses(session)
    return [_to_response(session, w) for w in warehouses]


def get_warehouse_by_id(session: Session, warehouse_id: UUID) -> Optional[WarehouseResponse]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None
    return _to_response(session, warehouse)


def update_warehouse(
    session: Session, warehouse_id: UUID, payload
) -> Optional[WarehouseResponse]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(warehouse, key, value)

    saved = warehouse_repository.save_warehouse(session, warehouse)
    return _to_response(session, saved)


def delete_warehouse(session: Session, warehouse_id: UUID) -> Optional[Warehouse]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    warehouse.is_active = False
    warehouse.deleted_at = datetime.utcnow()
    return warehouse_repository.save_warehouse(session, warehouse)
