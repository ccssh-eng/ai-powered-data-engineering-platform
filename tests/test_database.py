
import pytest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database.models import Base, Customer
from database.load import load_customers


@pytest.fixture
def test_db(monkeypatch):

    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    # Replace the production session with an isolated test session
    monkeypatch.setattr(
        "database.load.SessionLocal",
        TestSessionLocal
    )

    yield TestSessionLocal

    engine.dispose()


def test_insert_customer(test_db):

    customers = [
        {
            "id": 101,
            "name": "John Doe",
            "email": "john@example.com"
        }
    ]

    result = load_customers(customers)

    assert result == 1

    with test_db() as session:
        customer = session.get(Customer, 101)

        assert customer is not None
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"


def test_update_existing_customer(test_db):

    with test_db() as session:
        session.add(
            Customer(
                id=102,
                name="Old Name",
                email="old@example.com"
            )
        )
        session.commit()

    customers = [
        {
            "id": 102,
            "name": "New Name",
            "email": "new@example.com"
        }
    ]

    result = load_customers(customers)

    assert result == 1

    with test_db() as session:
        customer = session.get(Customer, 102)

        assert customer.name == "New Name"
        assert customer.email == "new@example.com"


def test_rollback_on_duplicate_email(test_db):

    customers = [
        {
            "id": 103,
            "name": "Customer One",
            "email": "duplicate@example.com"
        },
        {
            "id": 104,
            "name": "Customer Two",
            "email": "duplicate@example.com"
        }
    ]

    with pytest.raises(Exception):
        load_customers(customers)

    with test_db() as session:
        customers_in_db = session.scalars(
            select(Customer)
        ).all()

        assert len(customers_in_db) == 0


def test_empty_customer_list(test_db):

    result = load_customers([])

    assert result == 0

    with test_db() as session:
        customers = session.scalars(
            select(Customer)
        ).all()

        assert len(customers) == 0
