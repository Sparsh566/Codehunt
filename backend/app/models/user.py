import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="learner")  # learner, fisherman, captain, tourism_operator, admin
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    badges = Column(String(500), default="[]")  # JSON-encoded array of badge IDs
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_login = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
