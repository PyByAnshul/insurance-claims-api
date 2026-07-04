import io
import pandas as pd


CUSTOMER_REQUIRED = {"customer_id", "name", "age", "city", "state"}
POLICY_REQUIRED = {"policy_id", "customer_id", "policy_issue_date", "coverage_limit", "deductible", "state"}
CLAIM_REQUIRED = {"claim_id", "policy_id", "loss_date", "loss_amount", "cause"}


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df.map(lambda x: x.strip() if isinstance(x, str) else x)


def _validate_columns(df: pd.DataFrame, required: set[str]) -> list[str]:
    missing = required - set(df.columns)
    return [f"Missing required column: {c}" for c in missing]


def clean_customers(content: bytes) -> tuple[pd.DataFrame, list[str]]:
    df = _standardize(pd.read_csv(io.BytesIO(content)))
    errors = _validate_columns(df, CUSTOMER_REQUIRED)
    if errors:
        return pd.DataFrame(), errors

    df = df.dropna(subset=list(CUSTOMER_REQUIRED))
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    invalid = df["age"].isna() | (df["age"] <= 0)
    errors += [f"Invalid age for customer_id={r}" for r in df.loc[invalid, "customer_id"]]
    df = df[~invalid].drop_duplicates(subset=["customer_id"])
    df["age"] = df["age"].astype(int)
    return df, errors


def clean_policies(content: bytes) -> tuple[pd.DataFrame, list[str]]:
    df = _standardize(pd.read_csv(io.BytesIO(content)))
    errors = _validate_columns(df, POLICY_REQUIRED)
    if errors:
        return pd.DataFrame(), errors

    df = df.dropna(subset=list(POLICY_REQUIRED))
    df["policy_issue_date"] = pd.to_datetime(df["policy_issue_date"], errors="coerce")
    df["coverage_limit"] = pd.to_numeric(df["coverage_limit"], errors="coerce")
    df["deductible"] = pd.to_numeric(df["deductible"], errors="coerce")
    invalid = df["policy_issue_date"].isna() | df["coverage_limit"].isna() | df["deductible"].isna()
    errors += [f"Invalid data for policy_id={r}" for r in df.loc[invalid, "policy_id"]]
    df = df[~invalid].drop_duplicates(subset=["policy_id"])
    df["deductible"] = df["deductible"].astype(int)
    return df, errors


def clean_claims(content: bytes) -> tuple[pd.DataFrame, list[str]]:
    df = _standardize(pd.read_csv(io.BytesIO(content)))
    errors = _validate_columns(df, CLAIM_REQUIRED)
    if errors:
        return pd.DataFrame(), errors

    df = df.dropna(subset=list(CLAIM_REQUIRED))
    df["loss_date"] = pd.to_datetime(df["loss_date"], errors="coerce")
    df["loss_amount"] = pd.to_numeric(df["loss_amount"], errors="coerce")
    invalid = df["loss_date"].isna() | df["loss_amount"].isna()
    errors += [f"Invalid data for claim_id={r}" for r in df.loc[invalid, "claim_id"]]
    df = df[~invalid].drop_duplicates(subset=["claim_id"])
    return df, errors
