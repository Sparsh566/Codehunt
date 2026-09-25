import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from backend.app.db.session import Base

class LearnQuestion(Base):
    __tablename__ = "learn_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(500), nullable=False)
    options_json = Column(Text, nullable=False)  # JSON-encoded list of strings
    correct_answer = Column(String(200), nullable=False)
    hint = Column(String(300), nullable=True)
    explanation = Column(Text, nullable=False)
    category = Column(String(100), default="General Ocean Literacy")
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    points = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
