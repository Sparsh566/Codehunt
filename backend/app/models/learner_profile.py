import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from backend.app.db.session import Base

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    # 4 Pillar Literacy Scores (0 - 100%)
    ocean_conditions_mastery = Column(Float, default=0.0)  # wave/wind/swell reading
    safety_awareness_mastery = Column(Float, default=0.0)  # rough seas & storm response
    pfz_understanding_mastery = Column(Float, default=0.0) # potential fishing zones & SST
    advisory_compliance_mastery = Column(Float, default=0.0) # INCOIS alert obedience
    
    total_decisions = Column(Integer, default=0)
    quiz_attempts = Column(Integer, default=0)
    quiz_high_score = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
