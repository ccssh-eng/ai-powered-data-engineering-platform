import pytest

from transformation.transform import transform_customers


def test_valid_customer():

    customers = [
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@test.com"
        }
    ]

    result = transform_customers(customers)

    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_missing_email():

    customers = [
        {
            "id": 2,
            "name": "Bob"
        }
    ]

    result = transform_customers(customers)

    assert len(result) == 0


def test_name_cleanup():

    customers = [
        {
            "id": 3,
            "name": "  Charlie  ",
            "email": "charlie@test.com"
        }
    ]

    result = transform_customers(customers)

    assert result[0]["name"] == "Charlie"


def test_email_normalization():

    customers = [
        {
            "id": 4,
            "name": "David",
            "email": "DAVID@TEST.COM"
        }
    ]

    result = transform_customers(customers)

    assert result[0]["email"] == "david@test.com"


def test_invalid_customer_record():

    customers = [
        None,
        "invalid",
        123
    ]

    result = transform_customers(customers)

    assert result == []


def test_empty_customer_list():

    result = transform_customers([])

    assert result == []
