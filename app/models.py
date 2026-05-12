from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"
    customerNumber = Column(Integer, primary_key=True)
    customerName = Column(String(50), nullable=False)
    contactLastName = Column(String(50), nullable=False)
    contactFirstName = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)

    orders = relationship("Order", back_populates="customer")
    payments = relationship("Payment", back_populates="customer") 

class Order(Base):
    __tablename__ = "orders"
    orderNumber = Column(Integer, primary_key=True)
    orderDate = Column(Date, nullable=False)
    status = Column(String(15), nullable=False)
    customerNumber = Column(Integer, ForeignKey("customers.customerNumber"), nullable=False)

    customer = relationship("Customer", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "orderdetails"
    # Composite Primary Key
    orderNumber = Column(Integer, ForeignKey("orders.orderNumber"), primary_key=True)
    productCode = Column(String(15), primary_key=True)
    quantityOrdered = Column(Integer, nullable=False)
    priceEach = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="details")


class Payment(Base):
    __tablename__ = "payments"

    # Composite Primary Key: Both are marked primary_key=True
    customerNumber = Column(Integer, ForeignKey("customers.customerNumber"), primary_key=True)
    checkNumber = Column(String(50), primary_key=True)
    
    paymentDate = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    # Relationship back to the Customer
    customer = relationship("Customer", back_populates="payments")  