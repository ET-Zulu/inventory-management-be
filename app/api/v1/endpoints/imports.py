import csv
from io import StringIO

from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.model.item import Item
from app.model.vendor import Vendor
from app.model.bulk_import import BulkImport

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/csv")
def upload_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):

    content = file.file.read().decode("utf-8")
    csv_data = csv.DictReader(StringIO(content))

    errors = []
    valid_rows = []
 
    for index, row in enumerate(csv_data, start=1):

        sku = row.get("sku")
        name = row.get("name")
        vendor_id = row.get("vendor_id")
        cost_price = row.get("cost_price")
        selling_price = row.get("selling_price")
 
        if not sku:
            errors.append({"row": index, "field": "sku", "message": "Missing SKU"})
            continue

        if not name:
            errors.append({"row": index, "field": "name", "message": "Missing name"})
            continue

        if not vendor_id:
            errors.append({"row": index, "field": "vendor_id", "message": "Missing vendor"})
            continue
 
        vendor = session.exec(
            select(Vendor).where(
                Vendor.id == vendor_id,
                Vendor.is_active == True
            )
        ).first()

        if not vendor:
            errors.append({"row": index, "field": "vendor_id", "message": "Vendor not found"})
            continue
 
        existing_item = session.exec(
            select(Item).where(Item.sku == sku)
        ).first()

        if existing_item:
            errors.append({"row": index, "field": "sku", "message": "Duplicate SKU"})
            continue

        valid_rows.append(row)
 
    if errors:
        return {
            "status": "failed",
            "errors": errors
        }

    try:
        with session.begin():  

            for row in valid_rows:
                item = Item(
                    sku=row["sku"],
                    name=row["name"],
                    vendor_id=row["vendor_id"],
                    cost_price=float(row["cost_price"]),
                    selling_price=float(row["selling_price"]),
                )
                session.add(item)
 
            import_record = BulkImport(
                file_name=file.filename,
                records_processed=len(valid_rows),
                status="success"
            )

            session.add(import_record)

        return {
            "status": "success",
            "records": len(valid_rows)
        }

    except Exception as e:
        session.rollback()
        return {
            "status": "failed",
            "errors": [{"message": str(e)}]
        }