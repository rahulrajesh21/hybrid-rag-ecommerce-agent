from pydantic import BaseModel, ConfigDict, EmailStr

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    order_number: str
    item_name: str
    amount: float

class OrderOut(OrderCreate):
    id: int
    customer_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)