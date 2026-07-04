from sqlalchemy.orm import Session
from app.models.models import Policy


class PolicyRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, policy_id: int) -> Policy | None:
        return self._db.get(Policy, policy_id)

    def get_existing_ids(self, ids: list[int]) -> set[int]:
        rows = self._db.query(Policy.policy_id).filter(Policy.policy_id.in_(ids)).all()
        return {r[0] for r in rows}

    def bulk_insert(self, policies: list[Policy]) -> None:
        self._db.bulk_save_objects(policies)
        self._db.flush()
