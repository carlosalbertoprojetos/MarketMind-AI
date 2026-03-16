from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.analytics_engine import AnalyticsSummary, summarize


@dataclass(slots=True)
class AnalyticsAgent:
    db: Session

    def run(self, organization_id) -> AnalyticsSummary:
        return summarize(self.db, organization_id)