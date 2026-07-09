from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from sqlmodel import Session

from app.model.bin import Bin
from app.repository import bin_repository, warehouse_repository
from app.schemas.bin import BinResponse


def _to_response(session: Session, bin_: Bin) -> BinResponse:
    return BinResponse(
        id=bin_.id,
        warehouse_id=bin_.warehouse_id,
        name=bin_.name,
        is_system=bin_.is_system,
        created_at=bin_.created_at,
        items_count=bin_repository.count_items_in_bin(session, bin_.id),
    )


def create_bin(session: Session, warehouse_id: UUID, payload) -> Optional[BinResponse]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    existing = bin_repository.get_bin_by_name(session, warehouse_id, payload.name)
    if existing:
        raise ValueError(f"Bin '{payload.name}' already exists in this warehouse")

    bin_ = Bin(warehouse_id=warehouse_id, name=payload.name.strip())
    saved = bin_repository.save_bin(session, bin_)
    return _to_response(session, saved)


def get_bins(
    session: Session,
    warehouse_id: UUID,
    *,
    page: int = 1,
    limit: int = 20,
) -> Optional[Dict]:
    warehouse = warehouse_repository.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None

    bins, total = bin_repository.get_filtered_bins(session, warehouse_id, page, limit)
    return {
        "data": [_to_response(session, bin_) for bin_ in bins],
        "page": page,
        "limit": limit,
        "total": total,
    }


def get_bin(session: Session, warehouse_id: UUID, bin_id: UUID) -> Optional[BinResponse]:
    bin_ = bin_repository.get_bin_by_id(session, bin_id)
    if not bin_ or bin_.warehouse_id != warehouse_id:
        return None
    return _to_response(session, bin_)


def update_bin(session: Session, warehouse_id: UUID, bin_id: UUID, payload) -> Optional[BinResponse]:
    bin_ = bin_repository.get_bin_by_id(session, bin_id)
    if not bin_ or bin_.warehouse_id != warehouse_id:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] is not None:
        name = update_data["name"].strip()
        existing = bin_repository.get_bin_by_name(session, warehouse_id, name)
        if existing and existing.id != bin_.id:
            raise ValueError(f"Bin '{name}' already exists in this warehouse")
        bin_.name = name

    saved = bin_repository.save_bin(session, bin_)
    return _to_response(session, saved)


def delete_bin(session: Session, warehouse_id: UUID, bin_id: UUID) -> Optional[Bin]:
    bin_ = bin_repository.get_bin_by_id(session, bin_id)
    if not bin_ or bin_.warehouse_id != warehouse_id:
        return None

    if bin_.is_system:
        raise ValueError("General Storage cannot be deleted.")

    item_count = bin_repository.count_items_in_bin(session, bin_.id)
    if item_count > 0:
        raise ValueError(f"Cannot delete bin because it contains {item_count} active item(s).")

    bin_.deleted_at = datetime.utcnow()
    return bin_repository.save_bin(session, bin_)
