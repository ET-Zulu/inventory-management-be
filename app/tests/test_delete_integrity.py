from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.model.bin import Bin
from app.model.category import Category
from app.model.item import Item
from app.model.transaction import Transaction
from app.model.user import User
from app.model.vendor import Vendor
from app.model.warehouse import Warehouse
from app.model.enums import Itemtype, TransactionType, UserRole
from app.schemas.item import ItemCreate
from app.service import bin_service, category_service, item_service, vendor_service, warehouse_service


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    session.close()
    engine.dispose()


def _bin_for(session: Session, warehouse: Warehouse, *, name: str = "General Storage", is_system: bool = True) -> Bin:
    bin_ = Bin(warehouse_id=warehouse.id, name=name, is_system=is_system)
    session.add(bin_)
    session.commit()
    session.refresh(bin_)
    return bin_


def test_item_creation_requires_existing_active_vendor_and_warehouse(session: Session):
    payload = ItemCreate(
        sku="SKU-200",
        name="Laptop",
        description="Test item",
        initial_stock=1,
        minimum_stock_level=1,
        cost_price=100.0,
        selling_price=150.0,
        category_id=None,
        vendor_id=uuid4(),
        warehouse_id=uuid4(),
        bin_location="A1",
    )

    with pytest.raises(ValueError, match="vendor"):
        item_service.create_item(session, payload)


def test_category_delete_blocks_when_items_exist(session: Session):
    category = Category(name="Electronics", is_active=True)
    session.add(category)
    session.commit()
    session.refresh(category)

    vendor = Vendor(name="Vendor", contact_person="Jane", contact_info="x", location="L1")
    warehouse = Warehouse(name="WH1-category", location="Loc1")
    session.add_all([vendor, warehouse])
    session.commit()
    session.refresh(vendor)
    session.refresh(warehouse)
    bin_ = _bin_for(session, warehouse)

    item = Item(
        sku="SKU-100",
        name="Laptop",
        quantity_on_hand=2,
        cost_price=100.0,
        selling_price=150.0,
        category_id=category.id,
        vendor_id=vendor.id,
        bin_id=bin_.id,
        item_type=Itemtype.SALLABLE,
        is_active=True,
    )
    session.add(item)
    session.commit()

    with pytest.raises(ValueError, match="referenced"):
        category_service.delete_category(session, category.id)


def test_vendor_delete_blocks_when_items_exist(session: Session):
    vendor = Vendor(name="Vendor", contact_person="Jane", contact_info="x", location="L1")
    session.add(vendor)
    session.commit()
    session.refresh(vendor)

    warehouse = Warehouse(name="WH1-vendor", location="Loc1")
    session.add(warehouse)
    session.commit()
    session.refresh(warehouse)
    bin_ = _bin_for(session, warehouse)

    item = Item(
        sku="SKU-101",
        name="Laptop",
        quantity_on_hand=1,
        cost_price=100.0,
        selling_price=150.0,
        category_id=None,
        vendor_id=vendor.id,
        bin_id=bin_.id,
        item_type=Itemtype.SALLABLE,
        is_active=True,
    )
    session.add(item)
    session.commit()

    with pytest.raises(ValueError, match="referenced"):
        vendor_service.delete_vendor_service(session, vendor.id)


def test_warehouse_delete_blocks_when_bins_exist(session: Session):
    warehouse = Warehouse(name="WH1-warehouse", location="Loc1")
    session.add(warehouse)
    session.commit()
    session.refresh(warehouse)
    _bin_for(session, warehouse)

    with pytest.raises(ValueError, match="bin"):
        warehouse_service.delete_warehouse(session, warehouse.id)


def test_bin_delete_blocks_general_storage(session: Session):
    warehouse = Warehouse(name="WH1-system-bin", location="Loc1")
    session.add(warehouse)
    session.commit()
    session.refresh(warehouse)
    bin_ = _bin_for(session, warehouse)

    with pytest.raises(ValueError, match="General Storage"):
        bin_service.delete_bin(session, warehouse.id, bin_.id)


def test_bin_delete_blocks_when_items_exist(session: Session):
    vendor = Vendor(name="Vendor", contact_person="Jane", contact_info="x", location="L1")
    warehouse = Warehouse(name="WH1-bin-item", location="Loc1")
    session.add_all([vendor, warehouse])
    session.commit()
    session.refresh(vendor)
    session.refresh(warehouse)
    bin_ = _bin_for(session, warehouse, name="A1", is_system=False)

    item = Item(
        sku="SKU-102",
        name="Laptop",
        quantity_on_hand=1,
        cost_price=100.0,
        selling_price=150.0,
        vendor_id=vendor.id,
        bin_id=bin_.id,
        item_type=Itemtype.SALLABLE,
        is_active=True,
    )
    session.add(item)
    session.commit()

    with pytest.raises(ValueError, match="contains"):
        bin_service.delete_bin(session, warehouse.id, bin_.id)


def test_item_delete_soft_deletes_when_transactions_exist(session: Session):
    vendor = Vendor(name="Vendor", contact_person="Jane", contact_info="x", location="L1")
    warehouse = Warehouse(name="WH1-item", location="Loc1")
    session.add_all([vendor, warehouse])
    session.commit()
    session.refresh(vendor)
    session.refresh(warehouse)
    bin_ = _bin_for(session, warehouse)

    user = User(name="User", email="user@example.com", password_hash="x", role=UserRole.ADMIN, is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)

    item = Item(
        sku="SKU-103",
        name="Laptop",
        quantity_on_hand=1,
        cost_price=100.0,
        selling_price=150.0,
        category_id=None,
        vendor_id=vendor.id,
        bin_id=bin_.id,
        item_type=Itemtype.SALLABLE,
        is_active=True,
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    transaction = Transaction(
        item_id=item.id,
        user_id=user.id,
        transaction_type=TransactionType.INBOUND,
        quantity_change=1,
        before_quantity=0,
        after_quantity=1,
    )
    session.add(transaction)
    session.commit()

    deleted_item, action = item_service.delete_item(session, item.id)

    assert deleted_item is not None
    assert action == "soft_deleted"
    assert deleted_item.is_active is False
