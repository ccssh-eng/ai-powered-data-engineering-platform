
import pytest
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.connection import engine as postgres_engine
from database.connection import test_connection as check_postgres_connection
from database.models import Customer
from database.load import load_customers


@pytest.fixture
def postgres_db(monkeypatch):
    """Use a real PostgreSQL connection with rollback isolation."""

    assert postgres_engine.dialect.name == "postgresql"

    connection = postgres_engine.connect()
    transaction = connection.begin()

    try:
        result = connection.execute(
            text("SELECT 1")
        ).scalar_one()

        assert result == 1

        TestSessionLocal = sessionmaker(
            bind=connection,
            autoflush=False,
            autocommit=False,
            join_transaction_mode="create_savepoint"
        )

        monkeypatch.setattr(
            "database.load.SessionLocal",
            TestSessionLocal
        )

        yield TestSessionLocal

    finally:
        if transaction.is_active:
            transaction.rollback()

        connection.close()


def test_real_postgresql_connection():
    assert check_postgres_connection() is True


def test_insert_customer_postgresql(postgres_db):

    email = f"{uuid4().hex}@integration.test"

    customers = [{
        "id": -910001,
        "name": "Integration Customer",
        "email": email
    }]

    result = load_customers(customers)

    assert result == 1

    with postgres_db() as session:
        customer = session.get(Customer, -910001)

        assert customer is not None
        assert customer.name == "Integration Customer"
        assert customer.email == email


def test_update_customer_postgresql(postgres_db):

    email = f"{uuid4().hex}@integration.test"

    load_customers([{
        "id": -910002,
        "name": "Old Name",
        "email": email
    }])

    updated_email = f"{uuid4().hex}@integration.test"

    load_customers([{
        "id": -910002,
        "name": "New Name",
        "email": updated_email
    }])

    with postgres_db() as session:
        customer = session.get(Customer, -910002)

        assert customer.name == "New Name"
        assert customer.email == updated_email


def test_duplicate_email_rollback_postgresql(postgres_db):

    email = f"{uuid4().hex}@integration.test"

    customers = [
        {
            "id": -910003,
            "name": "Customer One",
            "email": email
        },
        {
            "id": -910004,
            "name": "Customer Two",
            "email": email
        }
    ]

    with pytest.raises(IntegrityError):
        load_customers(customers)

    with postgres_db() as session:
        result = session.scalars(
            select(Customer).where(
                Customer.email == email
            )
        ).all()

        assert len(result) == 0


def test_empty_customer_list_postgresql(postgres_db):

    result = load_customers([])

    assert result == 0
