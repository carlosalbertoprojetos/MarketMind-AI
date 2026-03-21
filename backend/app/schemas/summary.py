"""Schema de resumo do dashboard (estatísticas do usuário)."""
from pydantic import BaseModel


class UserSummaryResponse(BaseModel):
    total_campaigns: int
    by_platform: dict[str, int]  # ex: {"instagram": 2, "facebook": 1}
    upcoming_count: int  # campanhas agendadas nas próximas 24h
