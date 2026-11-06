
import logging

from ingestion.extract import extract_customers
from transformation.transform import transform_customers
from database.connection import test_connection
from database.load import load_customers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


def run_pipeline():

    logging.info("Starting Customer ETL Pipeline")

    if not test_connection():
        raise RuntimeError("PostgreSQL is unavailable")

    raw_customers = extract_customers()

    clean_customers = transform_customers(raw_customers)

    loaded_count = load_customers(clean_customers)

    logging.info(
        "Pipeline completed successfully: %s customers processed",
        loaded_count
    )

    return loaded_count


if __name__ == "__main__":
    run_pipeline()
