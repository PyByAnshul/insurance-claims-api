from datetime import date
from pydantic import BaseModel


class CustomerSchema(BaseModel):
    customer_id: str
    name: str
    age: int
    city: str
    state: str

    model_config = {"from_attributes": True}


class PolicySchema(BaseModel):
    policy_id: str
    customer_id: str
    policy_issue_date: date
    coverage_limit: float
    deductible: int
    state: str

    model_config = {"from_attributes": True}


class ClaimSchema(BaseModel):
    claim_id: str
    policy_id: str
    loss_date: date
    loss_amount: float
    cause: str
    final_payout: float
    fraud_flag: bool

    model_config = {"from_attributes": True}


class ClaimDetailResponse(BaseModel):
    claim: ClaimSchema
    customer: CustomerSchema
    policy: PolicySchema
    calculated_payout: float


class UploadResponse(BaseModel):
    total_records: int
    inserted: int
    rejected: int
    errors: list[str]


class TopCustomerSchema(BaseModel):
    customer_id: str
    name: str
    city: str
    state: str
    total_payout: float


class StateReportSchema(BaseModel):
    state: str
    total_claims: int
    average_payout: float
    maximum_payout: float
    total_payout: float


class HealthResponse(BaseModel):
    status: str
    database: str
    uptime: str
