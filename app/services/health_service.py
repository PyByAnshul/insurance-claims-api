from datetime import datetime
from app.models.database import check_db_connection
from app.schemas.schemas import HealthResponse

_start_time = datetime.utcnow()


class HealthService:
    def get_health(self) -> HealthResponse:
        db_ok = check_db_connection()
        uptime = self._format_uptime()
        return HealthResponse(
            status="healthy",
            database="connected" if db_ok else "disconnected",
            uptime=uptime,
        )

    def _format_uptime(self) -> str:
        delta = datetime.utcnow() - _start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
