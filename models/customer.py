from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_no = Column(String, primary_key=True)
    customer_name = Column(String)
    industry = Column(String)
    sales_region = Column(String)
    st_state = Column(String)
    st_city = Column(String)
    consumables_segment = Column(String)
    capital_segment = Column(String)
    npi_tercile = Column(String)
    account_age_months = Column(Integer)
    csat_score = Column(Float)
    customer_profile = Column(String)
    first_transaction_date = Column(Date)
    last_transaction_date = Column(Date)
    sales_inactivity_days = Column(Integer)
    churn_flag = Column(String)

    transactions = relationship("Transaction", back_populates="customer")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sales_ta_id = Column(Integer)
    customer_no = Column(String, ForeignKey("customers.customer_no"))
    product = Column(String)
    product_gbu = Column(String)
    product_main_grp = Column(String)
    transaction_date = Column(Date)
    quantity = Column(Float)
    amount = Column(Float)
    gross_margin = Column(Float)
    cost = Column(Float)
    invoice_type = Column(String)
    sales_region = Column(String)
    sales_territory = Column(String)
    sales_rep = Column(String)

    customer = relationship("Customer", back_populates="transactions")
