from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from db.db import SessionLocal
from db.db_model import Customer, Order
from sqlalchemy.orm import Session
from datetime import date,timedelta

@tool
def get_order_status(order_id: int | None = None, config: RunnableConfig = None):
    configurable = config.get("configurable", {}) if config else {}
    target_order_id = order_id or configurable.get("order_id")
    customer_id = configurable.get("customer_id")

    db = SessionLocal()
    try:
        query = db.query(Order).filter(Order.id == target_order_id)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        order = query.first()

        if not order:
            return f"No order found with ID {target_order_id}."
        return (
            f"Order #{order.order_number}: {order.item_name} | "
            f"Status: {order.status} | Amount: ${order.amount:.2f}"
        )
    finally:
        db.close()

def add_working_days(start_date: date, days: int) -> date:
    """Add N business days (skipping Saturday and Sunday) to start_date."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon=0 ... Fri=4
            added += 1
    return current

@tool
def delivery_estimate(order_id: int | None = None, config: RunnableConfig = None) -> str:
    """Estimate the delivery date for the customer's active order based on its order date and shipping tier."""
    configurable = config.get("configurable", {}) if config else {}
    target_order_id = order_id or configurable.get("order_id")
    customer_id = configurable.get("customer_id")

    if not target_order_id:
        return "Missing order_id in session context."

    db = SessionLocal()
    try:
        query = db.query(Order).filter(Order.id == target_order_id)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        order = query.first()

        if not order:
            return f"No order found with ID {target_order_id}."

        if order.status == "delivered":
            return f"Order #{order.order_number} has already been delivered."
        if order.status == "cancelled":
            return f"Order #{order.order_number} was cancelled and will not be delivered."

        # Fallback to today if date happens to be None
        base_date = getattr(order, "date", None) or getattr(order, "order_date", None) or date.today()
        tier = (order.shipping_tier or "standard").lower()

        if tier == "express":
            min_date = add_working_days(base_date, 3)
            max_date = add_working_days(base_date, 4)
            return (
                f"Order #{order.order_number} ({order.item_name}) uses Express shipping "
                f"(3–4 working days from {base_date.strftime('%b %d, %Y')}). "
                f"Estimated delivery: {min_date.strftime('%b %d, %Y')} – {max_date.strftime('%b %d, %Y')}."
            )

        # Standard shipping: 7 working days
        est_date = add_working_days(base_date, 7)
        return (
            f"Order #{order.order_number} ({order.item_name}) uses Standard shipping "
            f"(7 working days from {base_date.strftime('%b %d, %Y')}). "
            f"Estimated delivery: {est_date.strftime('%b %d, %Y')}."
        )
    finally:
        db.close()
from datetime import date
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from db.db import SessionLocal
from db.db_model import Order


@tool
def check_return_eligibility(order_id: int | None = None, config: RunnableConfig = None) -> str:
    """Checks whether an order is eligible for return and refund based on NovaGear's 30-day return policy.
    
    Args:
        order_id: Optional integer ID of the order. If omitted, reads from the active session context.
    """
    configurable = config.get("configurable", {}) if config else {}
    target_order_id = order_id or configurable.get("order_id")
    customer_id = configurable.get("customer_id")

    if not target_order_id:
        return "Please provide an order ID to verify return eligibility."

    db = SessionLocal()
    try:
        query = db.query(Order).filter(Order.id == target_order_id)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        order = query.first()

        if not order:
            return f"No order found with ID {target_order_id}."
        
        status = (order.status or "").lower()
        if status in ["cancelled", "canceled"]:
            return f"Order #{order.order_number} ({order.item_name}) was cancelled and cannot be returned."
        if status in ["returned", "refunded"]:
            return f"Order #{order.order_number} ({order.item_name}) has already been returned or refunded."
        if status == "processing":
            return (
                f"Order #{order.order_number} ({order.item_name}) is still processing and has not shipped yet. "
                f"You can cancel it directly for an immediate full refund rather than waiting for a return."
            )


        order_date = getattr(order, "date", None) or date.today()
        days_elapsed = (date.today() - order_date).days
        standard_window = 30

        is_electronics = any(
            keyword in order.item_name.lower()
            for keyword in ["buds", "hub", "lightbar", "charger", "audio", "sensor"]
        )

        if days_elapsed <= standard_window:
            days_remaining = standard_window - days_elapsed
            policy_notes = (
                f"Order #{order.order_number} ({order.item_name}) was placed on {order_date.strftime('%b %d, %Y')} "
                f"({days_elapsed} days ago). It is ELIGIBLE for return with {days_remaining} days remaining in the 30-day window.\n\n"
                f"• Return Options: 100% Free return shipping if you choose Store Credit or an exchange; "
                f"a flat $7.99 carrier label fee is deducted if refunding to your original payment method.\n"
            )
            if is_electronics:
                policy_notes += "• Note: Opened electronics must be returned within 14 days of delivery with all original accessories."
            return policy_notes
        days_overdue = days_elapsed - standard_window
        return (
            f"Order #{order.order_number} ({order.item_name}) was placed on {order_date.strftime('%b %d, %Y')} "
            f"({days_elapsed} days ago), which is {days_overdue} days past NovaGear's 30-day standard return window.\n\n"
            f"While standard returns have closed, your product is protected under NovaGear's 2-Year Limited Hardware Warranty. "
            f"If you are experiencing any technical defects or hardware malfunctions, we can initiate a warranty repair or replacement."
        )
    finally:
        db.close()
        