from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app
from app.core.database import get_session
from app.dependencies.auth import get_current_active_user
from app.model.bin import Bin
from app.model.category import Category
from app.model.item import Item
from app.model.vendor import Vendor
from app.model.warehouse import Warehouse
from app.model.enums import Itemtype

sqlite_file_name = "sqlite:///./test_category_totals.db"
engine = create_engine(sqlite_file_name, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_active_user] = lambda: SimpleNamespace(is_active=True)


def setup_function():
    SQLModel.metadata.create_all(engine)


def teardown_function():
    SQLModel.metadata.drop_all(engine)


def test_category_total_routes_are_distinct():
    with Session(engine) as session:
        category = Category(name="Electronics", is_active=True)
        session.add(category)
        session.commit()
        session.refresh(category)
        category_id = category.id

        vendor = Vendor(name="Vendor", contact_person="Jane", contact_info="x", location="L1")
        warehouse = Warehouse(name="WH1", location="Loc1")
        session.add_all([vendor, warehouse])
        session.commit()
        session.refresh(vendor)
        session.refresh(warehouse)

        bin_ = Bin(warehouse_id=warehouse.id, name="General Storage", is_system=True)
        session.add(bin_)
        session.commit()
        session.refresh(bin_)

        item = Item(
            sku="SKU-1",
            name="Laptop",
            quantity_on_hand=5,
            cost_price=100.0,
            selling_price=150.0,
            category_id=category_id,
            vendor_id=vendor.id,
            bin_id=bin_.id,
            item_type=Itemtype.SALLABLE,
            is_active=True,
        )
        session.add(item)
        session.commit()

    client = TestClient(app)

    aggregate_response = client.get("/api/v1/categories/total-items")
    assert aggregate_response.status_code == 200
    assert aggregate_response.json()["data"]["total_items"] == 5

    detail_response = client.get(f"/api/v1/categories/{category_id}/total-items")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["total_items"] == 5
