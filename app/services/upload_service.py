from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.models.models import Claim, Customer, Policy
from app.repositories import ClaimRepository, CustomerRepository, PolicyRepository
from app.schemas.schemas import UploadResponse
from app.services.payout_service import PayoutService
from app.utils.csv_cleaner import clean_claims, clean_customers, clean_policies

logger = get_logger(__name__)


class UploadService:
    def __init__(self, db: Session):
        self._db = db
        self._customer_repo = CustomerRepository(db)
        self._policy_repo = PolicyRepository(db)
        self._claim_repo = ClaimRepository(db)
        self._payout_service = PayoutService()

    def process(
        self,
        customer_bytes: bytes,
        policy_bytes: bytes,
        claims_bytes: bytes,
    ) -> UploadResponse:
        errors: list[str] = []
        total = 0
        inserted = 0

        cust_df, cust_errors = clean_customers(customer_bytes)
        errors.extend(cust_errors)
        cust_inserted, cust_rejected_errors = self._insert_customers(cust_df)
        errors.extend(cust_rejected_errors)
        total += len(cust_df) + len(cust_errors)
        inserted += cust_inserted

        pol_df, pol_errors = clean_policies(policy_bytes)
        errors.extend(pol_errors)
        pol_inserted, pol_rejected_errors = self._insert_policies(pol_df)
        errors.extend(pol_rejected_errors)
        total += len(pol_df) + len(pol_errors)
        inserted += pol_inserted

        claim_df, claim_errors = clean_claims(claims_bytes)
        errors.extend(claim_errors)
        claim_inserted, claim_rejected_errors = self._insert_claims(claim_df)
        errors.extend(claim_rejected_errors)
        total += len(claim_df) + len(claim_errors)
        inserted += claim_inserted

        self._db.commit()
        for e in errors:
            logger.warning("Rejected: %s", e)
        logger.info("Upload complete: total=%d inserted=%d rejected=%d", total, inserted, total - inserted)
        return UploadResponse(total_records=total, inserted=inserted, rejected=total - inserted, errors=errors)

    def _insert_customers(self, df) -> tuple[int, list[str]]:
        if df.empty:
            return 0, []
        existing = self._customer_repo.get_existing_ids(df["customer_id"].tolist())
        errors = []
        to_insert = []
        for _, row in df.iterrows():
            if row["customer_id"] in existing:
                errors.append(f"Duplicate customer_id={row['customer_id']}")
                continue
            to_insert.append(Customer(
                customer_id=row["customer_id"],
                name=row["name"],
                age=int(row["age"]),
                city=row["city"],
                state=row["state"],
            ))
        self._customer_repo.bulk_insert(to_insert)
        return len(to_insert), errors

    def _insert_policies(self, df) -> tuple[int, list[str]]:
        if df.empty:
            return 0, []
        existing_policies = self._policy_repo.get_existing_ids(df["policy_id"].tolist())
        valid_customers = self._customer_repo.get_existing_ids(df["customer_id"].tolist())
        errors = []
        to_insert = []
        for _, row in df.iterrows():
            if row["policy_id"] in existing_policies:
                errors.append(f"Duplicate policy_id={row['policy_id']}")
                continue
            if row["customer_id"] not in valid_customers:
                errors.append(f"policy_id={row['policy_id']} references missing customer_id={row['customer_id']}")
                continue
            to_insert.append(Policy(
                policy_id=row["policy_id"],
                customer_id=row["customer_id"],
                policy_issue_date=row["policy_issue_date"].date(),
                coverage_limit=float(row["coverage_limit"]),
                deductible=int(row["deductible"]),
                state=row["state"],
            ))
        self._policy_repo.bulk_insert(to_insert)
        return len(to_insert), errors

    def _insert_claims(self, df) -> tuple[int, list[str]]:
        if df.empty:
            return 0, []
        existing_claims = self._claim_repo.get_existing_ids(df["claim_id"].tolist())
        errors = []
        to_insert = []
        for _, row in df.iterrows():
            if row["claim_id"] in existing_claims:
                errors.append(f"Duplicate claim_id={row['claim_id']}")
                continue
            policy = self._policy_repo.get_by_id(row["policy_id"])
            if not policy:
                errors.append(f"claim_id={row['claim_id']} references missing policy_id={row['policy_id']}")
                continue
            rule_errors = self._payout_service.validate_claim_rules(
                float(row["loss_amount"]),
                row["loss_date"].date(),
                policy.policy_issue_date,
            )
            if rule_errors:
                errors.extend([f"claim_id={row['claim_id']}: {e}" for e in rule_errors])
                continue
            customer = self._customer_repo.get_by_id(policy.customer_id)
            claim_count = self._claim_repo.count_by_policy_customer(policy.customer_id)
            fraud_flag = self._payout_service.apply_fraud_flag(claim_count)
            temp_claim = Claim(
                claim_id=row["claim_id"],
                policy_id=row["policy_id"],
                loss_date=row["loss_date"].date(),
                loss_amount=float(row["loss_amount"]),
                cause=row["cause"],
                final_payout=0.0,
                fraud_flag=fraud_flag,
            )
            payout = self._payout_service.calculate(temp_claim, customer, policy)
            temp_claim.final_payout = payout
            to_insert.append(temp_claim)
        self._claim_repo.bulk_insert(to_insert)
        return len(to_insert), errors
