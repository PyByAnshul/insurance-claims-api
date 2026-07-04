from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.schemas import ClaimDetailResponse, ClaimSchema
from app.services.claim_service import ClaimService

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get(
    "/{claim_id}",
    response_model=ClaimDetailResponse,
    summary="Get claim details",
    description="Returns full claim, customer, policy info and calculated payout.",
    responses={404: {"description": "Claim not found"}},
)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    return ClaimService(db).get_detail(claim_id)


@router.get(
    "",
    response_model=list[ClaimSchema],
    summary="Search claims",
    description="Filter claims by city, state, cause, date range, and payout range. Supports sorting.",
)
def search_claims(
    city: str | None = Query(None),
    state: str | None = Query(None),
    cause: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    min_payout: float | None = Query(None),
    max_payout: float | None = Query(None),
    sort_by: str = Query("claim_id", pattern="^(claim_id|loss_date|final_payout|loss_amount)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    return ClaimService(db).search(city, state, cause, date_from, date_to, min_payout, max_payout, sort_by, sort_order)
