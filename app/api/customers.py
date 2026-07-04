from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.schemas import TopCustomerSchema
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "/top",
    response_model=list[TopCustomerSchema],
    summary="Top customers by payout",
    description="Returns top N customers ranked by total final payout.",
)
def top_customers(
    n: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return CustomerService(db).get_top_customers(n)
