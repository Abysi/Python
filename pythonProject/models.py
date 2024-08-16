import sqlalchemy
from typing import List
from database2 import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    first_name = sqlalchemy.Column(sqlalchemy.String)
    last_name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    registration_date = sqlalchemy.Column(sqlalchemy.DateTime)
    total_spend = sqlalchemy.Column(sqlalchemy.Float)
    last_purchase_date = sqlalchemy.Column(sqlalchemy.DateTime)

    def __init__(self, customer_id=None, first_name=None, last_name=None, email=None, registration_date=None, total_spend=None, last_purchase_date=None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.registration_date = registration_date
        self.total_spend = total_spend
        self.last_purchase_date = last_purchase_date

    def get_properties_string(self):
        return ', '.join([column.name for column in sqlalchemy.inspect(self.__class__).c])

