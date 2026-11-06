
import logging

from database.connection import SessionLocal
from database.models import Customer

logger = logging.getLogger(__name__)


def load_customers(customers):
    """
    Load transformed customers into PostgreSQL.

    Existing customers are updated using their primary key.
    """

    session = SessionLocal()

    try:
        loaded_count = 0

        with session.begin():

            for customer in customers:

                db_customer = Customer(
                    id=customer["id"],
                    name=customer["name"],
                    email=customer["email"]
                )

                session.merge(db_customer)
                loaded_count += 1

        logger.info(
            "Successfully loaded %s customers into PostgreSQL",
            loaded_count
        )

        return loaded_count

    except Exception:
        logger.exception("Customer loading failed")
        raise

    finally:
        session.close()
