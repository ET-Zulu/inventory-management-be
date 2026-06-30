from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_admin
from app.model.user import User
from app.schemas.bulk_import import ImportHistoryResponse

from app.service.import_service import (
    process_csv_import,
    get_import_history_service,
    search_import_history_service,
)

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/csv")
def upload_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    return process_csv_import(session, file, current_user.id)


@router.get("/history", response_model=list[ImportHistoryResponse], dependencies=[Depends(get_admin)])
def get_history(
    page: int = 1,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    imports = get_import_history_service(session, page, limit)

    return [
        ImportHistoryResponse(
            file_name=i.file_name,
            date=i.created_at,
            records=i.records_processed,
            status=i.status.value,
            file_link=i.file_link
        )
        for i in imports
    ]


@router.get("/history/search", response_model=list[ImportHistoryResponse], dependencies=[Depends(get_admin)])
def search_history(
    q: str = Query(...),
    session: Session = Depends(get_session)
):
    results = search_import_history_service(session, q)

    return [
        ImportHistoryResponse(
            file_name=i.file_name,
            date=i.created_at,
            records=i.records_processed,
            status=i.status.value,
            file_link=i.file_link
        )
        for i in results
    ]