import json
from sqlalchemy.orm import Session

from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models.user import User
from backend.app.models.question import LearnQuestion
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.scenario import ScenarioRecord
from backend.app.utils.security import hash_password

INITIAL_QUESTIONS = [
    {
        "question_text": "What percentage of Earth's surface is covered by oceans?",
        "options": ["50%", "60%", "70%", "80%"],
        "correct_answer": "70%",
        "hint": "It covers more than two-thirds of our entire planet.",
        "explanation": "Oceans cover approximately 70% of Earth's surface, acting as the primary climate regulator and supporting marine ecosystems.",
        "category": "Ocean Geography",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question_text": "Which ocean current is called the 'Global Conveyor Belt'?",
        "options": ["Gulf Stream", "Thermohaline Circulation", "El Niño", "Kuroshio Current"],
        "correct_answer": "Thermohaline Circulation",
        "hint": "It drives deep ocean circulation across all global basins based on temperature and salinity.",
        "explanation": "The Thermohaline Circulation moves heat and dense deep water globally, dictating continental climates and global nutrient cycles.",
        "category": "Ocean Currents & Climate",
        "difficulty": "medium",
        "points": 10
    },
    {
        "question_text": "What is ocean acidification mainly caused by?",
        "options": ["Oil spills", "Plastic pollution", "CO2 absorption", "Volcanoes"],
        "correct_answer": "CO2 absorption",
        "hint": "It is directly linked to human carbon emissions into the atmosphere.",
        "explanation": "Oceans absorb roughly 30% of anthropogenic CO2, forming carbonic acid which lowers pH levels and harms calcifying organisms.",
        "category": "Ocean Chemistry",
        "difficulty": "medium",
        "points": 10
    },
    {
        "question_text": "Which marine ecosystem has the highest biodiversity?",
        "options": ["Deep sea vents", "Mangroves", "Coral reefs", "Open ocean"],
        "correct_answer": "Coral reefs",
        "hint": "Often nicknamed the 'underwater rainforests'.",
        "explanation": "Coral reefs shelter over 25% of all marine species despite covering less than 0.1% of the total ocean floor.",
        "category": "Marine Biology",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question_text": "Which is the largest ocean on Earth?",
        "options": ["Indian Ocean", "Atlantic Ocean", "Pacific Ocean", "Arctic Ocean"],
        "correct_answer": "Pacific Ocean",
        "hint": "It spans more than 30% of the Earth's surface and is larger than all landmasses combined.",
        "explanation": "The Pacific Ocean is both the largest and deepest ocean basin on Earth, containing the Mariana Trench.",
        "category": "Ocean Geography",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question_text": "What is the primary cause of rising sea levels?",
        "options": ["Tectonic activity", "Volcanic eruptions", "Melting ice caps and thermal expansion", "Underwater earthquakes"],
        "correct_answer": "Melting ice caps and thermal expansion",
        "hint": "Global warming causes both ice melt and the physical expansion of warming seawater.",
        "explanation": "Rising sea levels are primarily driven by thermal expansion of warming ocean water and the melting of terrestrial ice sheets and glaciers.",
        "category": "Climate Impact",
        "difficulty": "medium",
        "points": 10
    },
    {
        "question_text": "Which marine mammal is known as the 'canary of the sea'?",
        "options": ["Dolphin", "Blue Whale", "Beluga Whale", "Sea Otter"],
        "correct_answer": "Beluga Whale",
        "hint": "Known for high-pitched bird-like vocal chirps and whistles.",
        "explanation": "Beluga Whales produce diverse vocalizations (clicks, whistles, squeals) earning them the nickname 'canaries of the sea'.",
        "category": "Marine Species",
        "difficulty": "hard",
        "points": 10
    },
    {
        "question_text": "What is the name of the deepest surveyed oceanic trench on Earth?",
        "options": ["Mariana Trench", "Puerto Rico Trench", "Java Trench", "Tonga Trench"],
        "correct_answer": "Mariana Trench",
        "hint": "The Challenger Deep inside this trench plunges to nearly 11,000 meters depth.",
        "explanation": "The Mariana Trench in the western Pacific reaches a maximum depth of approximately 10,994 meters at Challenger Deep.",
        "category": "Deep Ocean",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question_text": "What is bioluminescence in marine life?",
        "options": ["Underwater electrical discharge", "Light emission produced via chemical reactions", "Pressure reflection phenomenon", "Phosphorus pollution"],
        "correct_answer": "Light emission produced via chemical reactions",
        "hint": "Luciferin and luciferase react together to emit blue-green glow in the twilight zone.",
        "explanation": "Bioluminescence is light generated by a biochemical reaction inside an organism, vital for deep-sea hunting, camouflage, and communication.",
        "category": "Marine Biology",
        "difficulty": "medium",
        "points": 10
    },
    {
        "question_text": "Which microscopic marine organisms produce over 50% of the oxygen we breathe?",
        "options": ["Marine Kelp", "Phytoplankton", "Coral Zooxanthellae", "Sea Grasses"],
        "correct_answer": "Phytoplankton",
        "hint": "Microscopic photosynthetic drift organisms found floating in surface waters.",
        "explanation": "Phytoplankton produce between 50% and 80% of the oxygen in Earth's atmosphere through oceanic photosynthesis.",
        "category": "Marine Ecology",
        "difficulty": "medium",
        "points": 10
    }
]

def init_db():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Seed Admin & Demo User
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Seeding admin user...")
            admin_user = User(
                username="admin",
                email="admin@incois.gov.in",
                hashed_password=hash_password("admin123"),
                role="admin",
                is_admin=True,
                xp=1000,
                level=5,
                current_streak=7,
                badges=json.dumps(["incois_certified", "fleet_commander"])
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Leaderboard & Profile
            db.add(LeaderboardEntry(
                user_id=admin_user.id,
                username="admin",
                role="admin",
                total_score=850,
                scenarios_completed=12,
                safe_decisions_count=12,
                accuracy_percentage=100,
                rank=1
            ))
            db.add(LearnerProfile(
                user_id=admin_user.id,
                ocean_conditions_mastery=95.0,
                safety_awareness_mastery=100.0,
                pfz_understanding_mastery=92.0,
                advisory_compliance_mastery=100.0,
                total_decisions=12,
                quiz_attempts=5,
                quiz_high_score=100
            ))
            db.commit()

        # Seed Demo User
        demo_user = db.query(User).filter(User.username == "captain_vikram").first()
        if not demo_user:
            print("Seeding demo user captain_vikram...")
            demo_user = User(
                username="captain_vikram",
                email="vikram@ocean.in",
                hashed_password=hash_password("sailor123"),
                role="ship_captain",
                is_admin=False,
                xp=420,
                level=2,
                current_streak=3,
                badges=json.dumps(["welcome_sailor", "rough_sea_survivor"])
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            
            db.add(LeaderboardEntry(
                user_id=demo_user.id,
                username="captain_vikram",
                role="ship_captain",
                total_score=420,
                scenarios_completed=5,
                safe_decisions_count=4,
                accuracy_percentage=80,
                rank=2
            ))
            db.add(LearnerProfile(
                user_id=demo_user.id,
                ocean_conditions_mastery=82.0,
                safety_awareness_mastery=88.0,
                pfz_understanding_mastery=70.0,
                advisory_compliance_mastery=85.0,
                total_decisions=5,
                quiz_attempts=2,
                quiz_high_score=90
            ))
            db.commit()

        # Seed Learn Questions
        existing_q_count = db.query(LearnQuestion).count()
        if existing_q_count == 0:
            print("Seeding 10 ocean literacy questions...")
            for q_data in INITIAL_QUESTIONS:
                q = LearnQuestion(
                    question_text=q_data["question_text"],
                    options_json=json.dumps(q_data["options"]),
                    correct_answer=q_data["correct_answer"],
                    hint=q_data["hint"],
                    explanation=q_data["explanation"],
                    category=q_data["category"],
                    difficulty=q_data["difficulty"],
                    points=q_data["points"],
                    is_active=True
                )
                db.add(q)
            db.commit()
            print(f"Successfully seeded {len(INITIAL_QUESTIONS)} questions.")
        else:
            print(f"Database already contains {existing_q_count} questions.")

        # Seed/Sync Play Mode Scenarios
        import os
        from pathlib import Path
        fixtures_path = Path(__file__).resolve().parent.parent.parent / "fixtures" / "scenarios.json"
        if fixtures_path.exists():
            with open(fixtures_path, "r", encoding="utf-8") as f:
                scenarios_data = json.load(f)
            
            for sc in scenarios_data:
                existing_record = db.query(ScenarioRecord).filter(ScenarioRecord.scenario_code == sc["scenario_code"]).first()
                if not existing_record:
                    record = ScenarioRecord(
                        scenario_code=sc["scenario_code"],
                        role=sc["role"],
                        title=sc["title"],
                        location=sc["location"],
                        narrative=sc["narrative"],
                        wave_height_m=sc["ocean_data"]["wave_height_m"],
                        wind_speed_knots=sc["ocean_data"]["wind_speed_knots"],
                        swell_period_sec=sc["ocean_data"].get("swell_period_sec", 10.0),
                        sea_surface_temp_c=sc["ocean_data"].get("sea_surface_temp_c", 28.0),
                        pfz_zone_active=sc["ocean_data"].get("pfz_zone_active", False),
                        incois_warning_type=sc["ocean_data"].get("incois_warning_type", "none"),
                        incois_alert_level=sc["ocean_data"].get("incois_alert_level", "GREEN"),
                        options_json=json.dumps(sc["options"]),
                        recommended_action_id=sc["recommended_action_id"],
                        consequences_json=json.dumps(sc["consequences"]),
                        is_active=True
                    )
                    db.add(record)
                else:
                    existing_record.role = sc["role"]
                    existing_record.title = sc["title"]
                    existing_record.narrative = sc["narrative"]
                    existing_record.options_json = json.dumps(sc["options"])
                    existing_record.consequences_json = json.dumps(sc["consequences"])
                    existing_record.recommended_action_id = sc["recommended_action_id"]
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
