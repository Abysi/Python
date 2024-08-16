import csv
from database2 import Session
import io
import models
import schemas
from datetime import datetime
from sqlalchemy import func


def export_customers(db: Session):
    return db.query(models.Customer).all()

def export_customers_to_csv(customers: models.Customer):
    stream = io.StringIO()
    writer = csv.writer(stream)
    customer = models.Customer()
    customer_props = customer.get_properties_string()
    columns = customer_props.split(', ')
    writer.writerow(columns)
    for customer in customers:
        row = [getattr(customer, column) for column in columns]
        writer.writerow(row)
    stream.seek(0)
    return stream

def import_customers_from_csv(file):
    customers = []
    reader = csv.DictReader(file.read().decode('utf-8').splitlines())
    try:
        for row in reader:
            customers.append(schemas.Customer(**row))
    except Exception as e:
        raise Exception('Invalid CSV file.')
    return customers

def upsert_customers(db: Session, customers: list[schemas.Customer]):
    for customer in customers:
        customer_data = customer.dict()
        db.merge(models.Customer(**customer_data))
    db.commit()


def get_customers_analytics(db: Session, start_date: datetime, end_date: datetime ):
    total_customers = db.query(models.Customer).count()
    average_total_spend = db.query(func.avg(models.Customer.total_spend)).scalar()
    active_customers = db.query(models.Customer).filter(
        models.Customer.last_purchase_date.between(start_date, end_date)
    ).count()
    active_percentage = (active_customers / total_customers) * 100
    top_customers = []
    for customer in db.query(models.Customer).order_by(models.Customer.total_spend.desc()).limit(5).all():
        top_customers.append(schemas.TopCustomer(
            customer_id=customer.customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            total_spend=customer.total_spend))

    return schemas.AnalyticsResponse(
        average_total_spend=average_total_spend,
        active_customers_percentage=active_percentage,
        top_customers=top_customers
    )


