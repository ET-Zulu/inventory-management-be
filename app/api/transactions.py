from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db  
from app.schemas import SuccessResponse, success_response  
from app.schemas.transaction import TransactionCreateRequest
from app.service.transaction import TransactionService  

router = APIRouter()

@router.post("", response_model=SuccessResponse)
def create_transaction(
    payload: TransactionCreateRequest, 
    db: Session = Depends(get_db)
):
   
    result = TransactionService.create_inventory_transaction(db, payload)
    
    response_data = {
        "id": str(result.id),
        "user_id": str(result.user_id),
        "item_id": str(result.item_id),
        "transaction_type": result.transaction_type,
        "quantity_change": result.quantity_change,
        "reference_number": result.reference_number,
        "notes": result.notes,
        "before_quantity": result.before_quantity,
        "after_quantity": result.after_quantity,
        "created_at": result.created_at.isoformat()
    }
    return success_response(message="Operation completed", data=response_data)


@router.get("", response_model=SuccessResponse)
def list_transactions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    search: Optional[str] = Query(default=None, description="Search by item id, sku, or name"),
    type: Optional[str] = Query(default=None, description="Filter: inbound or outbound"),
    start_date: Optional[str] = Query(default=None, description="ISO Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="ISO Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    
    ledger_data = TransactionService.get_transaction_ledger(
        db=db,
        page=page,
        limit=limit,
        search=search,
        tx_type=type,
        start_date=start_date,
        end_date=end_date
    )
    return success_response(message="Operation completed", data=ledger_data)