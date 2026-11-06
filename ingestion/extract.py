
import logging
import requests

logger = logging.getLogger(__name__)

API_URL = "https://jsonplaceholder.typicode.com/users"


def extract_customers():
    """
    Extract customer data from JSONPlaceholder API.
    """

    try:
        logger.info("Starting customer data extraction")

        response = requests.get(
            API_URL,
            timeout=15
        )

        response.raise_for_status()

        customers = response.json()

        if not isinstance(customers, list):
            raise ValueError("Expected a list of customers")

        logger.info(
            "Successfully extracted %s customers",
            len(customers)
        )

        return customers

    except requests.RequestException:
        logger.exception("API extraction failed")
        raise

    except ValueError:
        logger.exception("Invalid API response")
        raise
