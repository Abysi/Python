import pytest
from unittest.mock import MagicMock
import io
import csv
from datetime import datetime
from utils import (
    export_customers,
    export_customers_to_csv,
    import_customers_from_csv,
    upsert_customers,
    get_customers_analytics
)
import models, schemas

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    return session

@pytest.fixture
def mock_customers():
    return [
        models.Customer(customer_id=1, first_name='John', last_name='Doe', total_spend=100, last_purchase_date=datetime(2023, 1, 1)),
        models.Customer(customer_id=2, first_name='Jane', last_name='Doe', total_spend=200, last_purchase_date=datetime(2023, 1, 2))
    ]
@pytest.fixture
def mock_csv():
    return """customer_id,first_name,last_name,total_spend,last_purchase_date
1,John,Doe,100,2023-01-01
2,Jane,Doe,200,2023-01-02
"""


def test_export_customers(mock_db_session, mock_customers):
    mock_db_session.query.return_value.all.return_value = mock_customers
    customers = export_customers(mock_db_session)
    assert customers == mock_customers

def test_export_customers_to_csv(mock_customers):
    stream = export_customers_to_csv(mock_customers)
    assert isinstance(stream, io.StringIO)
    reader = csv.reader(stream.getvalue().splitlines())
    headers = next(reader)
    assert headers == ['customer_id', 'first_name', 'last_name', 'total_spend', 'last_purchase_date']
    rows = list(reader)
    assert len(rows) == len(mock_customers)

def test_import_customers_from_csv():
    csv_content = mock_csv()
    file = io.BytesIO(csv_content.encode('utf-8'))
    customers = import_customers_from_csv(file)
    assert len(customers) == 2
    assert customers[0].first_name == 'John'

def test_upsert_customers(mock_db_session, mock_customers):
    schema_customers = [schemas.Customer.from_orm(c) for c in mock_customers]
    upsert_customers(mock_db_session, schema_customers)
    assert mock_db_session.merge.call_count == len(schema_customers)
    assert mock_db_session.commit.called

def test_get_customers_analytics(mock_db_session, mock_customers):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    mock_db_session.query.return_value.count.return_value = len(mock_customers)
    mock_db_session.query.return_value.scalar.return_value = sum(c.total_spend for c in mock_customers) / len(mock_customers)
    mock_db_session.query.return_value.filter.return_value.count.return_value = len(mock_customers) // 2
    mock_db_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = mock_customers[:5]

    analytics = get_customers_analytics(mock_db_session, start_date, end_date)
    assert analytics.average_total_spend == 150
    assert analytics.active_customers_percentage == 50.0
    assert len(analytics.top_customers) == 2