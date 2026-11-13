from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db
from db.db_model import Customer, Order
from models.models import CustomerCreate, CustomerOut, OrderCreate, OrderOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=CustomerOut)
def register_user(user: CustomerCreate, db: Session = Depends(get_db)):
    normalized_email = user.email.lower()
    existing = db.query(Customer).filter(Customer.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = Customer(
        name=user.name,
        email=normalized_email,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{customer_id}", response_model=CustomerOut)
def get_user(customer_id: int, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("",response_model=list[CustomerOut])
def get_user_list(db:Session=Depends(get_db)):
    return db.query(Customer).all()

@router.post("/{customer_id}/orders", response_model=OrderOut)
def create_order(customer_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_order = (
        db.query(Order).filter(Order.order_number == order.order_number).first()
    )
    if existing_order:
        raise HTTPException(status_code=400, detail="Order number already exists")

    db_order = Order(
        customer_id=customer_id,
        **order.model_dump(),
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/{customer_id}/orders", response_model=list[OrderOut])
def get_user_orders(customer_id: int, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Order).filter(Order.customer_id == customer_id).all()


@router.get("/{customer_id}/orders/{order_id}", response_model=OrderOut)
def get_order(customer_id: int, order_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.customer_id == customer_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{customer_id}/orders/{order_id}", response_model=OrderOut)
def update_order_status(
    customer_id: int, order_id: int, status: str, db: Session = Depends(get_db)
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.customer_id == customer_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found for this user")

    order.status = status
    db.commit()
    db.refresh(order)
    return order