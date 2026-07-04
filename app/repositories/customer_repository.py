from sqlalchemy.orm import Session
from app.models.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self._db.get(Customer, customer_id)

    def get_existing_ids(self, ids: list[int]) -> set[int]:
        rows = self._db.query(Customer.customer_id).filter(Customer.customer_id.in_(ids)).all()
        return {r[0] for r in rows}

    def bulk_insert(self, customers: list[Customer]) -> None:
        self._db.bulk_save_objects(customers)
        self._db.flush()
