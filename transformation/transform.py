import logging

logger = logging.getLogger(__name__)


def transform_customers(customers):
    """
    Clean and validate customer records.
    """

    transformed_customers = []

    for customer in customers:

        required_fields = ["id", "name", "email"]

        if not isinstance(customer, dict):
            logger.warning("Invalid customer record")
            continue

        if not all(customer.get(field) for field in required_fields):
            logger.warning(
                "Customer record rejected: missing required fields"
            )
            continue

        transformed_customer = {
            "id": customer["id"],
            "name": customer["name"].strip(),
            "email": customer["email"].strip().lower()
        }

        transformed_customers.append(transformed_customer)

    logger.info(
        "Transformation completed: %s records accepted, %s rejected",
        len(transformed_customers),
        len(customers) - len(transformed_customers)
    )

    return transformed_customers
