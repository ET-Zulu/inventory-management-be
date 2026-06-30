from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_current_active_user, get_operator
from app.schemas.transaction import (
    TransactionInput,
    TransactionCreateDataResponse,
    TransactionListDashboardResponse,
)
from app.service.transaction_service import (
    create_inventory_transaction,
    get_transaction_ledger,
)

router = APIRouter()


@router.post(
    "/",
    response_model=TransactionCreateDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new stock transaction ledger entry",
)
async def create_transaction(
    payload: TransactionInput,
    db: Session = Depends(get_session),
    current_user = Depends(get_operator),
):
    return await create_inventory_transaction(db=db, current_user=current_user, payload=payload)


@router.get(
    "/",
    response_model=TransactionListDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions with dashboard overview analytics",
    dependencies=[Depends(get_current_active_user)],
)
def list_transactions(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(
        None, description="Search by item name, SKU, or item ID"
    ),
    transaction_type: Optional[str] = Query(
        None, description="Filter by type: INBOUND or OUTBOUND"
    ),
    start_date: Optional[str] = Query(
        None, description="Filter from start date (ISO format)"
    ),
    end_date: Optional[str] = Query(
        None, description="Filter to end date (ISO format)"
    ),
    db: Session = Depends(get_session),
):
    return get_transaction_ledger(
        db=db,
        page=page,
        limit=limit,
        search=search,
        tx_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
    )
