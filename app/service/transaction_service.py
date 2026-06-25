from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session

from app.model.enums import TransactionType
from app.model.item import Item
from app.model.transaction import Transaction
from app.model.user import User
from app.repository.transaction_repository import (
    fetch_transaction_ledger,
    get_item_for_update,
    get_transaction_metrics,
    save_transaction,
)
from app.schemas.transaction import TransactionInput


def create_inventory_transaction(
    db: Session,
    current_user: User,
    payload: TransactionInput,
) -> Transaction:
    item = get_item_for_update(db, payload.item_id)
    if not item or not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target active inventory item could not be found.",
        )

    before_qty = item.quantity_on_hand
    if payload.transaction_type == TransactionType.INBOUND:
        after_qty = before_qty + payload.quantity_change
    elif payload.transaction_type == TransactionType.OUTBOUND:
        after_qty = before_qty - payload.quantity_change
        if after_qty < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INSUFFICIENT_STOCK",
                    "message": "Stock cannot go below zero",
                },
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported transaction type execution requested.",
        )

    item.quantity_on_hand = after_qty
    db.add(item)

    transaction = Transaction(
        item_id=payload.item_id,
        user_id=current_user.id,
        transaction_type=payload.transaction_type,
        quantity_change=payload.quantity_change,
        before_quantity=before_qty,
        after_quantity=after_qty,
        created_at=datetime.utcnow(),
    )

    return save_transaction(db, transaction)


def get_transaction_ledger(
    db: Session,
    page: int,
    limit: int,
    search: Optional[str] = None,
    tx_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    tx_filter: Optional[TransactionType] = None
    if tx_type:
        try:
            tx_filter = TransactionType(tx_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported transaction type filter provided.",
            )

    transactions = fetch_transaction_ledger(
        db,
        page=page,
        limit=limit,
        search=search,
        tx_type=tx_filter,
        start_date=start_date,
        end_date=end_date,
    )

    metrics = get_transaction_metrics(db, datetime.utcnow() - timedelta(hours=24))

    records = [
        {
            "id": tx.id,
            "item": tx.item.name,
            "sku": tx.item.sku,
            "transaction_type": tx.transaction_type,
            "quantity_change": tx.quantity_change,
            "Opratore_name": tx.user.name,
            # notes removed from DB schema; omit from output
            "before_quantity": tx.before_quantity,
            "after_quantity": tx.after_quantity,
            "created_at": tx.created_at,
        }
        for tx in transactions
    ]

    return {
        "total_movement": metrics["total_movement"],
        "inbound_24h": metrics["inbound_24h"],
        "outbound_24h": metrics["outbound_24h"],
        "anomalies": metrics["anomalies"],
        "data": records,
    }
