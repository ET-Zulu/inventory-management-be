from datetime import datetime, timedelta
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.model.enums import TransactionType
from app.model.item import Item  
from app.model.transaction import Transaction
from app.model.user import User  
from app.schemas import ErrorCode  
from app.schemas.transaction import TransactionCreateRequest


class TransactionService:

    @staticmethod
    def create_inventory_transaction(db: Session, payload: TransactionCreateRequest) -> Transaction:
        
        item = db.query(Item).filter(Item.id == payload.item_id).with_for_update().first()
        
        if not item or not item.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target active inventory item could not be found."
            )

        before_qty = item.stock

        if payload.transaction_type == TransactionType.INBOUND:
            after_qty = before_qty + payload.quantity_change
        elif payload.transaction_type == TransactionType.OUTBOUND:
            after_qty = before_qty - payload.quantity_change
            
            if after_qty < 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "INSUFFICIENT_STOCK",
                        "message": "Stock cannot go below zero"
                    }
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported transaction type execution requested."
            )

        item.stock = after_qty
        db.add(item)

        db_tx = Transaction(
            item_id=payload.item_id,
            user_id=payload.user_id,
            transaction_type=payload.transaction_type,
            quantity_change=payload.quantity_change,
            before_quantity=before_qty,
            after_quantity=after_qty,
            reference_number=payload.reference_number,
            notes=payload.notes,
            created_at=datetime.utcnow()
        )
        db.add(db_tx)
        
        db.commit()
        db.refresh(db_tx)
        return db_tx

    @staticmethod
    def get_transaction_ledger(
        db: Session,
        page: int,
        limit: int,
        search: Optional[str] = None,
        tx_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> dict:
        
        query = db.query(Transaction).join(Item).join(User)

        if search:
            query = query.filter(
                or_(
                    func.cast(Item.id, func.text).ilike(f"%{search}%"),
                    Item.sku.ilike(f"%{search}%"),
                    Item.name.ilike(f"%{search}%")
                )
            )

        if tx_type:
            query = query.filter(Transaction.transaction_type == tx_type.upper())

        if start_date:
            query = query.filter(Transaction.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Transaction.created_at <= datetime.fromisoformat(end_date))

        past_24h = datetime.utcnow() - timedelta(hours=24)
        
        total_movement = db.query(func.count(Transaction.id)).scalar() or 0
        
        inbound_24h = db.query(func.sum(Transaction.quantity_change)).filter(
            Transaction.transaction_type == TransactionType.INBOUND,
            Transaction.created_at >= past_24h
        ).scalar() or 0

        outbound_24h = db.query(func.sum(Transaction.quantity_change)).filter(
            Transaction.transaction_type == TransactionType.OUTBOUND,
            Transaction.created_at >= past_24h
        ).scalar() or 0

        anomalies = db.query(func.count(Transaction.id)).filter(
            Transaction.transaction_type == TransactionType.OUTBOUND,
            Transaction.quantity_change >= 100,
            Transaction.created_at >= past_24h
        ).scalar() or 0

        
        offset = (page - 1) * limit
        transactions_list = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

        
        records = []
        for tx in transactions_list:
            records.append({
                "id": tx.id,
                "item": tx.item.name,
                "sku": tx.item.sku,
                "transaction_type": tx.transaction_type,
                "quantity_change": tx.quantity_change,
                "operator_name": tx.user.name,  # Pulled cleanly via User join
                "reference_number": tx.reference_number,
                "notes": tx.notes,
                "before_quantity": tx.before_quantity,
                "after_quantity": tx.after_quantity,
                "created_at": tx.created_at
            })

        return {
            "total_movement": total_movement,
            "inbound_24h": int(inbound_24h),
            "outbound_24h": int(outbound_24h),
            "anomalies": anomalies,
            "data": records
        }