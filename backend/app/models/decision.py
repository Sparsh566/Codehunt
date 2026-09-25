import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from backend.app.db.session import Base

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), index=True, nullable=False)
    chosen_option_id = Column(String(50), nullable=False)
    
    # Deterministic Engine Output
    is_safe = Column(Boolean, nullable=False)
    score_delta = Column(Integer, nullable=False)
    vessel_status = Column(String(100), default="Intact")
    xp_awarded = Column(Integer, default=0)
    rule_feedback = Column(Text, nullable=True)
    
    # AI Explanation Layer (Generated post-verdict)
    ai_explanation = Column(Text, nullable=True)
    tavily_learn_more = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
