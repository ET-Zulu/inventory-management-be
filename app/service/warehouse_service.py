from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from sqlmodel import Session

from app.model.warehouse import Warehouse
from app.repository import bin_repository, warehouse_repository
from app.schemas.warehouse import WarehouseResponse


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
        existing.is_active = True
        existing.deleted_at = None
        existing.location = payload.location
        existing.capacity = payload.capacity
        existing.description = payload.description
        saved = warehouse_repository.save_warehouse(session, existing)
        bin_repository.ensure_general_storage_bin(session, saved.id)
        return saved

    warehouse = Warehouse(
        name=payload.name,
        location=payload.location,
        capacity=payload.capacity,
        description=payload.description,
    )
    saved = warehouse_repository.save_warehouse(session, warehouse)
    bin_repository.ensure_general_storage_bin(session, saved.id)
    return saved


def get_all_warehouses(
    session: Session,
    *,
    page: int = 1,
    limit: int = 20,
) -> Dict:
    warehouses, total = warehouse_repository.get_filtered_warehouses(session, page, limit)
    return {
        "data": [_to_response(session, w) for w in warehouses],
        "page": page,
        "limit": limit,
        "total": total,
    }


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


def get_warehouse_summary(session: Session, warehouse_id: UUID) -> Optional[dict]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    items = warehouse_repository.get_active_items_in_warehouse(session, warehouse_id)

    return {
        "warehouse_id": str(warehouse.id),
        "warehouse_name": warehouse.name,
        "total_items": len(items),
        "total_inventory_quantity": sum(item.quantity_on_hand for item in items),
        "low_stock_items": [item.id for item in items if item.quantity_on_hand <= item.minimum_stock_level],
        "items": [item.id for item in items],
    }


def delete_warehouse(session: Session, warehouse_id: UUID) -> Optional[Warehouse]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    bin_count = bin_repository.count_bins_in_warehouse(session, warehouse_id)
    if bin_count > 0:
        raise ValueError(
            f"Cannot delete warehouse because it still contains {bin_count} bin(s)."
        )

    warehouse.is_active = False
    warehouse.deleted_at = datetime.utcnow()
    return warehouse_repository.save_warehouse(session, warehouse)


def check_warehouse_name_availability(session: Session, name: str) -> Dict:
    name = name.strip()

    if not name:
        return {
            "name": name,
            "available": False,
            "message": "Warehouse name cannot be empty",
        }

    existing = warehouse_repository.get_warehouse_by_name(session, name)

    if existing and existing.is_active:
        return {
            "name": name,
            "available": False,
            "message": f"Warehouse '{name}' is already in use",
        }

    return {
        "name": name,
        "available": True,
        "message": f"Warehouse '{name}' is available",
    }


def get_total_items_per_warehouse_by_id(
    session: Session, warehouse_id: UUID
) -> Optional[Dict]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    total_items = warehouse_repository.count_items_in_warehouse(session, warehouse_id)

    return {
        "warehouse_id": warehouse.id,
        "warehouse_name": warehouse.name,
        "total_items": int(total_items or 0),
    }
