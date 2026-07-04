from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)

    policies: Mapped[list["Policy"]] = relationship("Policy", back_populates="customer")


class Policy(Base):
    __tablename__ = "policies"

    policy_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customers.customer_id"), nullable=False)
    policy_issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    coverage_limit: Mapped[float] = mapped_column(Float, nullable=False)
    deductible: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="policies")
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    claim_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    policy_id: Mapped[str] = mapped_column(String, ForeignKey("policies.policy_id"), nullable=False)
    loss_date: Mapped[date] = mapped_column(Date, nullable=False)
    loss_amount: Mapped[float] = mapped_column(Float, nullable=False)
    cause: Mapped[str] = mapped_column(String, nullable=False)
    final_payout: Mapped[float] = mapped_column(Float, nullable=False)
    fraud_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    policy: Mapped["Policy"] = relationship("Policy", back_populates="claims")


Index("ix_claims_cause", Claim.cause)
Index("ix_claims_loss_date", Claim.loss_date)
Index("ix_customers_state", Customer.state)
Index("ix_customers_city", Customer.city)
