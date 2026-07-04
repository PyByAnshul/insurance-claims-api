from datetime import date
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories import ClaimRepository, PolicyRepository
from app.schemas.schemas import ClaimDetailResponse, ClaimSchema, CustomerSchema, PolicySchema
from app.services.payout_service import PayoutService


class ClaimService:
    def __init__(self, db: Session):
        self._claim_repo = ClaimRepository(db)
        self._payout_service = PayoutService()

    def get_detail(self, claim_id: str) -> ClaimDetailResponse:
        claim = self._claim_repo.get_by_id(claim_id)
        if not claim:
            raise NotFoundException(f"Claim {claim_id} not found")
        policy = claim.policy
        customer = policy.customer
        payout = self._payout_service.calculate(claim, customer, policy)
        return ClaimDetailResponse(
            claim=ClaimSchema.model_validate(claim),
            customer=CustomerSchema.model_validate(customer),
            policy=PolicySchema.model_validate(policy),
            calculated_payout=payout,
        )

    def search(
        self,
        city: str | None,
        state: str | None,
        cause: str | None,
        date_from: date | None,
        date_to: date | None,
        min_payout: float | None,
        max_payout: float | None,
        sort_by: str,
        sort_order: str,
    ) -> list[ClaimSchema]:
        claims = self._claim_repo.search(city, state, cause, date_from, date_to, min_payout, max_payout, sort_by, sort_order)
        return [ClaimSchema.model_validate(c) for c in claims]
