import cloudinary
import cloudinary.uploader

import csv
from io import StringIO
from uuid import UUID

from sqlmodel import Session, select

from app.model.item import Item
from app.model.vendor import Vendor
from app.model.bulk_import import BulkImport
from app.model.enums import ImportStatus

from app.repository import warehouse_repository
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

    print(content)

    file.file.seek(0)

    upload_result = cloudinary.uploader.upload(
    file.file,
    resource_type="raw",
    folder="inventory-imports"
    )

    file_link = upload_result.get("secure_url")
    csv_data = csv.DictReader(StringIO(content))

    print(csv_data.fieldnames)

    errors = []
    valid_rows = []

    for index, row in enumerate(csv_data, start=1):

         # Skip completely empty rows
        if not any(value.strip() for value in row.values() if value):
                continue
        
        print(row)

        row_errors = []

        sku = row.get("sku", "").strip()
        name = row.get("name", "").strip()
        vendor_id = row.get("vendor_id", "").strip()
        item_type = row.get("item_type", "SALLABLE").strip().upper()

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
        
        if item_type not in ["SALLABLE", "NON_SALLABLE"]:
            row_errors.append({
                "row": index,
                "field": "item_type",
                "message": "Invalid item type. Must be 'SALLABLE' or 'NON_SALLABLE'"
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

            # print(row)

            if not row.get("location"):
                raise ValueError(f"Missing warehouse location for SKU '{row.get('sku')}'")

            existing = warehouse_repository.get_warehouse_by_name(session, row.get("location"))

            if not existing:
                raise ValueError(f"Warehouse '{row.get("location")}' does not exist")

            item = Item(
                sku=row["sku"],
                name=row["name"],
                vendor_id=row["vendor_id"],

                item_type=row.get("item_type", "SALLABLE").upper(),

                cost_price=float(row.get("cost_price", 0)),
                selling_price=float(row.get("selling_price", 0)),

                description=row.get("description"),
                location=row.get("location", ""),

                quantity_on_hand=int(row.get("quantity_on_hand", 0)),
                minimum_stock_level=int(row.get("minimum_stock_level", 0)),

                warehouse_id= existing.id,

                category_id=row.get("category_id") if row.get("category_id") else None
                
            )
            session.add(item)

        # Save import history
        bulk_import = BulkImport(
            file_name=file.filename,
            records_processed=len(valid_rows),
            status=ImportStatus.SUCCESS,
            uploaded_by=user_id,
            file_link=file_link
            
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