from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import cast, func, or_, String
from sqlmodel import Session, select, col, desc

from app.model.enums import TransactionType
from app.model.item import Item
from app.model.transaction import Transaction
from app.model.user import User


def get_item_for_update(session: Session, item_id: UUID) -> Optional[Item]:
    statement = select(Item).where(Item.id == item_id).with_for_update()
    return session.exec(statement).first()


def save_transaction(session: Session, transaction: Transaction) -> Transaction:
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def fetch_transaction_ledger(
    session: Session,
    page: int,
    limit: int,
    search: Optional[str] = None,
    tx_type: Optional[TransactionType] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[list[Transaction], int]:
    statement = select(Transaction).join(Item).join(User)
    count_statement = select(func.count()).select_from(Transaction)

    if search:
        search_text = f"%{search}%"
        filter_cond = or_(
            cast(Transaction.item_id, String).ilike(search_text),
            col(Item.sku).ilike(search_text),
            col(Item.name).ilike(search_text),
        )
        statement = statement.where(filter_cond)
        count_statement = count_statement.where(filter_cond)

    if tx_type:
        statement = statement.where(Transaction.transaction_type == tx_type)
        count_statement = count_statement.where(Transaction.transaction_type == tx_type)

    if start_date:
        dt = datetime.fromisoformat(start_date)
        statement = statement.where(Transaction.created_at >= dt)
        count_statement = count_statement.where(Transaction.created_at >= dt)

    if end_date:
        dt = datetime.fromisoformat(end_date)
        statement = statement.where(Transaction.created_at <= dt)
        count_statement = count_statement.where(Transaction.created_at <= dt)

    total = session.exec(count_statement).one()

    offset = (page - 1) * limit
    statement = (
        statement.order_by(desc(Transaction.created_at))
        .offset(offset)
        .limit(limit)
    )

    data = session.exec(statement).all()

    return data, total or 0


def _scalar_value(session: Session, statement) -> int:
    values = session.exec(statement).all()
    return int(values[0] or 0) if values else 0


def get_transaction_metrics(session: Session, past_24h: datetime) -> dict[str, int]:
    total_movement = _scalar_value(session, select(func.sum(Transaction.quantity_change)))

    inbound_24h = _scalar_value(
        session,
        select(func.sum(Transaction.quantity_change)).where(
            Transaction.transaction_type == TransactionType.INBOUND,
            Transaction.created_at >= past_24h,
        ),
    )

    outbound_24h = _scalar_value(
        session,
        select(func.sum(Transaction.quantity_change)).where(
            Transaction.transaction_type == TransactionType.OUTBOUND,
            Transaction.created_at >= past_24h,
        ),
    )

    anomalies = _scalar_value(
        session,
        select(func.count()).select_from(Transaction).where(
            Transaction.transaction_type == TransactionType.OUTBOUND,
            Transaction.quantity_change > 100,
            Transaction.created_at >= past_24h,
        ),
    )

    return {
        "total_movement": total_movement,
        "inbound_24h": inbound_24h,
        "outbound_24h": outbound_24h,
        "anomalies": anomalies,
    }
