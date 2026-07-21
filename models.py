import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

class PredictionModel:
    """Machine learning model for predictions"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def train(self, features, labels):
        """Train the model"""
        X = np.array(features)
        y = np.array(labels)
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
    def predict(self, features):
        """Make predictions"""
        if not self.model:
            return None
        
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)[0]
    
    def predict_proba(self, features):
        """Get prediction probabilities"""
        if not self.model:
            return None
        
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict_proba(X_scaled)[0]

class AnalyticsModel:
    """Analytics model for match insights"""
    
    @staticmethod
    def calculate_team_rating(stats):
        """Calculate team rating from statistics"""
        # Weighted metrics
        attack_score = stats.get('goals_for', 0) / max(1, stats.get('games_played', 1)) * 10
        defense_score = (1 - stats.get('goals_against', 0) / max(1, stats.get('games_played', 1)) * 0.5) * 10
        form_score = stats.get('form', '').count('W') * 2 + stats.get('form', '').count('D')
        
        return (attack_score + defense_score + form_score) / 3
    
    @staticmethod
    def predict_score(home_rating, away_rating):
        """Predict match score"""
        total_goals = (home_rating + away_rating) / 20
        home_goals = int(total_goals * (home_rating / (home_rating + away_rating)) * 2)
        away_goals = int(total_goals * (away_rating / (home_rating + away_rating)) * 2)
        
        return f"{home_goals}-{away_goals}"
    
    @staticmethod
    def calculate_confidence(home_prob, away_prob):
        """Calculate prediction confidence"""
        return abs(home_prob - away_prob)
