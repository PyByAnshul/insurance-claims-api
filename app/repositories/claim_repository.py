from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.models import Claim, Customer, Policy


class ClaimRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, claim_id: int) -> Claim | None:
        return (
            self._db.query(Claim)
            .options(joinedload(Claim.policy).joinedload(Policy.customer))
            .filter(Claim.claim_id == claim_id)
            .first()
        )

    def get_existing_ids(self, ids: list[int]) -> set[int]:
        rows = self._db.query(Claim.claim_id).filter(Claim.claim_id.in_(ids)).all()
        return {r[0] for r in rows}

    def count_by_policy_customer(self, customer_id: int) -> int:
        return (
            self._db.query(func.count(Claim.claim_id))
            .join(Policy, Claim.policy_id == Policy.policy_id)
            .filter(Policy.customer_id == customer_id)
            .scalar()
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
    ) -> list[Claim]:
        query = (
            self._db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.policy_id)
            .join(Customer, Policy.customer_id == Customer.customer_id)
        )
        if city:
            query = query.filter(Customer.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Policy.state.ilike(f"%{state}%"))
        if cause:
            query = query.filter(Claim.cause.ilike(f"%{cause}%"))
        if date_from:
            query = query.filter(Claim.loss_date >= date_from)
        if date_to:
            query = query.filter(Claim.loss_date <= date_to)
        if min_payout is not None:
            query = query.filter(Claim.final_payout >= min_payout)
        if max_payout is not None:
            query = query.filter(Claim.final_payout <= max_payout)

        sort_column = getattr(Claim, sort_by, Claim.claim_id)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        return query.order_by(sort_column).all()

    def bulk_insert(self, claims: list[Claim]) -> None:
        self._db.bulk_save_objects(claims)
        self._db.flush()
