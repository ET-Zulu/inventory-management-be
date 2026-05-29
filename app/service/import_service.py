import csv
from io import StringIO
from uuid import UUID

from sqlmodel import Session, select

from app.model.item import Item
from app.model.vendor import Vendor
from app.model.bulk_import import BulkImport
from app.model.enums import ImportStatus

from app.repository.import_repository import (
    get_import_history,
    search_import_history,
)


def process_csv_import(session: Session, file, user_id: UUID | None = None):
    """
    Process CSV import using all-or-nothing validation.

    SRS Rule:
    - If any row fails validation, nothing is saved.
    - If all rows are valid, all items are inserted and
      an import history record is created.
    """

    content = file.file.read().decode("utf-8")
    csv_data = csv.DictReader(StringIO(content))

    errors = []
    valid_rows = []

    for index, row in enumerate(csv_data, start=1):
        row_errors = []

        sku = row.get("sku")
        name = row.get("name")
        vendor_id = row.get("vendor_id")

        # Required field validation
        if not sku:
            row_errors.append({
                "row": index,
                "field": "sku",
                "message": "Missing SKU"
            })

        if not name:
            row_errors.append({
                "row": index,
                "field": "name",
                "message": "Missing name"
            })

        if not vendor_id:
            row_errors.append({
                "row": index,
                "field": "vendor_id",
                "message": "Missing vendor"
            })

        # Vendor validation
        if vendor_id:
            vendor = session.exec(
                select(Vendor).where(
                    Vendor.id == vendor_id,
                    Vendor.is_active == True
                )
            ).first()

            if not vendor:
                row_errors.append({
                    "row": index,
                    "field": "vendor_id",
                    "message": "Vendor not found"
                })

        # Duplicate SKU validation
        if sku:
            existing_item = session.exec(
                select(Item).where(Item.sku == sku)
            ).first()

            if existing_item:
                row_errors.append({
                    "row": index,
                    "field": "sku",
                    "message": "Duplicate SKU"
                })

        # Row-level decision
        if row_errors:
            errors.extend(row_errors)
        else:
            valid_rows.append(row)

    # Atomic validation rule
    if errors:
        return {
            "status": "failed",
            "errors": errors
        }

    try:
        # Insert all items
        for row in valid_rows:
            item = Item(
                sku=row["sku"],
                name=row["name"],
                vendor_id=row["vendor_id"],
                cost_price=float(row.get("cost_price", 0)),
                selling_price=float(row.get("selling_price", 0)),
            )
            session.add(item)

        # Save import history
        bulk_import = BulkImport(
            file_name=file.filename,
            records_processed=len(valid_rows),
            status=ImportStatus.SUCCESS,
            uploaded_by=user_id
        )

        session.add(bulk_import)

        # Commit everything atomically
        session.commit()

        return {
            "status": "success",
            "records": len(valid_rows)
        }

    except Exception as e:
        session.rollback()
        return {
            "status": "failed",
            "errors": [
                {
                    "message": str(e)
                }
            ]
        }


def get_import_history_service(session: Session, page: int, limit: int):
    skip = (page - 1) * limit
    return get_import_history(session, skip, limit)


def search_import_history_service(session: Session, query: str):
    return search_import_history(session, query)