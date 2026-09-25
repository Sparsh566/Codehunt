import json
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.question import LearnQuestion
from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.api.auth import get_current_user_optional

router = APIRouter(prefix="/api/learn", tags=["Learn Mode"])

class QuestionItem(BaseModel):
    id: int
    question: str
    options: List[str]
    hint: Optional[str]
    category: str
    points: int

class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: str

class QuizSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]

class QuestionResult(BaseModel):
    question_id: int
    question: str
    selected_option: str
    correct_answer: str
    is_correct: bool
    explanation: str
    points_earned: int

class QuizResultResponse(BaseModel):
    total_score: int
    max_score: int
    accuracy_percentage: int
    xp_earned: int
    results: List[QuestionResult]

@router.get("/questions", response_model=List[QuestionItem])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(LearnQuestion).filter(LearnQuestion.is_active == True).all()
    items = []
    for q in questions:
        try:
            opts = json.loads(q.options_json)
        except Exception:
            opts = []
        items.append(QuestionItem(
            id=q.id,
            question=q.question_text,
            options=opts,
            hint=q.hint,
            category=q.category,
            points=q.points
        ))
    return items

@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz(
    submission: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    questions = {q.id: q for q in db.query(LearnQuestion).all()}
    
    total_score = 0
    max_score = 0
    correct_count = 0
    results: List[QuestionResult] = []

    for ans in submission.answers:
        q = questions.get(ans.question_id)
        if not q:
            continue
        max_score += q.points
        is_corr = (ans.selected_option.strip() == q.correct_answer.strip())
        points = q.points if is_corr else 0
        if is_corr:
            correct_count += 1
            total_score += points
        
        results.append(QuestionResult(
            question_id=q.id,
            question=q.question_text,
            selected_option=ans.selected_option,
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            explanation=q.explanation,
            points_earned=points
        ))

    accuracy = int((correct_count / len(submission.answers) * 100)) if submission.answers else 0
    xp_earned = total_score * 2  # 2 XP per quiz point

    # Update authenticated user records if logged in
    if current_user:
        current_user.xp += xp_earned
        current_user.level = max(1, (current_user.xp // 250) + 1)
        
        # Update Leaderboard Entry
        lb = db.query(LeaderboardEntry).filter(LeaderboardEntry.user_id == current_user.id).first()
        if lb:
            lb.total_score += total_score
        
        # Update Learner Profile
        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
        if profile:
            profile.quiz_attempts += 1
            if total_score > profile.quiz_high_score:
                profile.quiz_high_score = total_score
            # Boost conditions and safety mastery based on quiz accuracy
            profile.ocean_conditions_mastery = min(100.0, profile.ocean_conditions_mastery + (accuracy * 0.15))
            profile.safety_awareness_mastery = min(100.0, profile.safety_awareness_mastery + (accuracy * 0.15))
        
        db.commit()

    return QuizResultResponse(
        total_score=total_score,
        max_score=max_score if max_score > 0 else 100,
        accuracy_percentage=accuracy,
        xp_earned=xp_earned,
        results=results
    )
