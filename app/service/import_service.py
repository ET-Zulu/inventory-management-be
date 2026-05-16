import csv
from io import StringIO
from sqlmodel import Session, select

from app.model.item import Item
from app.model.vendor import Vendor
from app.model.bulk_import import BulkImport
from app.repository.import_repository import save_bulk_import


def process_csv_import(session: Session, file, user_id: str):

    content = file.file.read().decode("utf-8")
    csv_data = csv.DictReader(StringIO(content))

    errors = []
    valid_rows = []

    for index, row in enumerate(csv_data, start=1):

        # REQUIRED FIELDS CHECK
        if not row.get("sku"):
            errors.append({
                "row": index,
                "field": "sku",
                "message": "Missing SKU"
            })

        if not row.get("name"):
            errors.append({
                "row": index,
                "field": "name",
                "message": "Missing name"
            })

        if not row.get("vendor_id"):
            errors.append({
                "row": index,
                "field": "vendor_id",
                "message": "Missing vendor"
            })

        vendor = session.exec(
            select(Vendor).where(Vendor.id == row.get("vendor_id"))
        ).first()

        if not vendor:
            errors.append({
                "row": index,
                "field": "vendor_id",
                "message": "Vendor not found"
            })

        if not errors:
            valid_rows.append(row)

    if errors:
        return {
            "status": "failed",
            "errors": errors
        }

    for row in valid_rows:
        item = Item(
            sku=row["sku"],
            name=row["name"],
            vendor_id=row["vendor_id"],
            cost_price=float(row.get("cost_price", 0)),
            selling_price=float(row.get("selling_price", 0)),
        )
        session.add(item)

    bulk_import = BulkImport(
        file_name=file.filename,
        records_processed=len(valid_rows),
        status="success",
        uploaded_by=user_id
    )

    save_bulk_import(session, bulk_import)

    session.commit()

    return {
        "status": "success",
        "records": len(valid_rows)
    }