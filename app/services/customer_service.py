from sqlalchemy import func, text
from sqlalchemy.orm import Session
from app.models.models import Claim, Customer, Policy
from app.schemas.schemas import TopCustomerSchema


class CustomerService:
    def __init__(self, db: Session):
        self._db = db

    def get_top_customers(self, n: int) -> list[TopCustomerSchema]:
        rows = (
            self._db.query(
                Customer.customer_id,
                Customer.name,
                Customer.city,
                Customer.state,
                func.sum(Claim.final_payout).label("total_payout"),
            )
            .join(Policy, Customer.customer_id == Policy.customer_id)
            .join(Claim, Policy.policy_id == Claim.policy_id)
            .group_by(Customer.customer_id)
            .order_by(func.sum(Claim.final_payout).desc())
            .limit(n)
            .all()
        )
        return [
            TopCustomerSchema(
                customer_id=r.customer_id,
                name=r.name,
                city=r.city,
                state=r.state,
                total_payout=round(r.total_payout, 2),
            )
            for r in rows
        ]
