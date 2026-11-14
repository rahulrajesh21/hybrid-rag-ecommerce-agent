from db.db import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String,Date
from sqlalchemy.orm import relationship
from datetime import date

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="processing")
    shipping_tier = Column(String, default="standard", nullable=False)
    date = Column(Date,default=date.today,nullable=False)
    customer = relationship("Customer", back_populates="orders")