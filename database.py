from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(200), unique=True)
    league = Column(String(100))
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    status = Column(String(50))  # scheduled, live, finished
    match_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class TeamStats(Base):
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    team = Column(String(100))
    league = Column(String(100))
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    form = Column(String(10))  # e.g., "WWLDD"
    points = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String(100))
    team = Column(String(100))
    league = Column(String(100))
    position = Column(String(50))
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(200))
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    predicted_score = Column(String(20))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

class Database:
    @staticmethod
    def get_session():
        return SessionLocal()
    
    @staticmethod
    def save_match(match_data):
        session = SessionLocal()
        try:
            match = Match(**match_data)
            session.add(match)
            session.commit()
        finally:
            session.close()
    
    @staticmethod
    def update_team_stats(team_data):
        session = SessionLocal()
        try:
            stat = session.query(TeamStats).filter_by(
                team=team_data['team'], 
                league=team_data['league']
            ).first()
            if stat:
                for key, value in team_data.items():
                    setattr(stat, key, value)
            else:
                stat = TeamStats(**team_data)
                session.add(stat)
            session.commit()
        finally:
            session.close()
