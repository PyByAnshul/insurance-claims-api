from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.schemas import StateReportSchema


class ReportService:
    def __init__(self, db: Session):
        self._db = db

    def get_state_report(self) -> list[StateReportSchema]:
        sql = text("""
            SELECT
                c.state,
                COUNT(cl.claim_id)        AS total_claims,
                AVG(cl.final_payout)      AS average_payout,
                MAX(cl.final_payout)      AS maximum_payout,
                SUM(cl.final_payout)      AS total_payout
            FROM claims cl
            JOIN policies p  ON cl.policy_id  = p.policy_id
            JOIN customers c ON p.customer_id = c.customer_id
            GROUP BY c.state
            ORDER BY total_payout DESC
        """)
        rows = self._db.execute(sql).fetchall()
        return [
            StateReportSchema(
                state=r.state,
                total_claims=r.total_claims,
                average_payout=round(r.average_payout, 2),
                maximum_payout=round(r.maximum_payout, 2),
                total_payout=round(r.total_payout, 2),
            )
            for r in rows
        ]

    def get_top_cities_by_payout(self, limit: int = 10) -> list[dict]:
        sql = text("""
            SELECT
                c.city,
                c.state,
                SUM(cl.final_payout) AS total_payout
            FROM claims cl
            JOIN policies p  ON cl.policy_id  = p.policy_id
            JOIN customers c ON p.customer_id = c.customer_id
            GROUP BY c.city, c.state
            ORDER BY total_payout DESC
            LIMIT :limit
        """)
        rows = self._db.execute(sql, {"limit": limit}).fetchall()
        return [{"city": r.city, "state": r.state, "total_payout": round(r.total_payout, 2)} for r in rows]
