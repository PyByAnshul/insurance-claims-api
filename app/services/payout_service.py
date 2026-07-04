from datetime import date
from app.models.models import Claim, Customer, Policy


class PayoutService:
    def calculate(self, claim: Claim, customer: Customer, policy: Policy) -> float:
        payout = min(claim.loss_amount, policy.coverage_limit) - policy.deductible
        payout = max(payout, 0.0)

        if customer.age < 18:
            payout *= 0.5

        if claim.cause.lower() == "flood" and policy.state.upper() == "CA":
            payout *= 0.90

        return round(payout, 2)

    def apply_fraud_flag(self, claim_count: int) -> bool:
        return claim_count > 5

    def validate_claim_rules(
        self, loss_amount: float, loss_date: date, policy_issue_date: date
    ) -> list[str]:
        errors = []
        if loss_amount < 0:
            errors.append("Loss amount cannot be negative")
        if loss_date > date.today():
            errors.append("Loss date cannot be in the future")
        if loss_date < policy_issue_date:
            errors.append("Loss date cannot be before policy issue date")
        return errors
