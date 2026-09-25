import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from backend.app.db.session import Base

class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    role = Column(String(50), default="all")
    total_score = Column(Integer, default=0, index=True)
    scenarios_completed = Column(Integer, default=0)
    safe_decisions_count = Column(Integer, default=0)
    accuracy_percentage = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_leaderboard_score_role", "role", "total_score"),
    )
