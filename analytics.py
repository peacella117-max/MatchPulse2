from datetime import datetime, timedelta
import random
from sports_api import SportsAPI
from database import Database
from models import AnalyticsModel

class MatchAnalytics:
    """Advanced match analytics engine"""
    
    def __init__(self):
        self.api = SportsAPI()
        self.db = Database()
        self.model = AnalyticsModel()
    
    def analyze_match(self, match_id=None, home_team=None, away_team=None):
        """Analyze a match"""
        if match_id:
            # Fetch match from API
            match_data = self.get_match(match_id)
        else:
            match_data = {'home_team': home_team, 'away_team': away_team}
        
        if not match_data:
            return None
        
        # Get team stats
        home_stats = self.get_team_analytics(match_data.get('home_team', ''))
        away_stats = self.get_team_analytics(match_data.get('away_team', ''))
        
        # Calculate metrics
        home_rating = self.model.calculate_team_rating(home_stats)
        away_rating = self.model.calculate_team_rating(away_stats)
        
        # Predict outcome
        total_rating = home_rating + away_rating
        if total_rating > 0:
            home_prob = (home_rating / total_rating) * 100
            away_prob = (away_rating / total_rating) * 100
        else:
            home_prob = 33.3
            away_prob = 33.3
        
        draw_prob = 100 - home_prob - away_prob
        
        # Predict score
        predicted_score = self.model.predict_score(home_rating, away_rating)
        
        # Calculate confidence
        confidence = self.model.calculate_confidence(home_prob, away_prob)
        
        return {
            'home_team': match_data.get('home_team', ''),
            'away_team': match_data.get('away_team', ''),
            'home_rating': round(home_rating, 1),
            'away_rating': round(away_rating, 1),
            'home_prob': round(home_prob, 1),
            'draw_prob': round(draw_prob, 1),
            'away_prob': round(away_prob, 1),
            'predicted_score': predicted_score,
            'confidence': round(confidence, 1),
            'home_form': home_stats.get('form', 'LWWD'),
            'away_form': away_stats.get('form', 'DWWL'),
            'home_stats': home_stats,
            'away_stats': away_stats
        }
    
    def get_team_analytics(self, team_name):
        """Get detailed team analytics"""
        # In production, this would query a real database
        # For demo, generate synthetic data
        return {
            'games_played': random.randint(10, 30),
            'wins': random.randint(4, 15),
            'draws': random.randint(2, 8),
            'losses': random.randint(2, 8),
            'goals_for': random.randint(15, 50),
            'goals_against': random.randint(10, 35),
            'form': ''.join(random.choice(['W', 'D', 'L']) for _ in range(5)),
            'points': random.randint(20, 50)
        }
    
    def get_match(self, match_id):
        """Get match from API"""
        matches = self.api.get_live_matches()
        for match in matches:
            if match.get('id') == match_id:
                return match
        return None
    
    def format_full_analytics(self, analytics):
        """Format full analytics report"""
        if not analytics:
            return "No analytics available"
        
        home_form_analysis = self.analyze_form(analytics.get('home_form', ''))
        away_form_analysis = self.analyze_form(analytics.get('away_form', ''))
        
        message = f"""
📊 *FULL MATCH ANALYTICS*
━━━━━━━━━━━━━━━━━━━━━

🔵 *{analytics['home_team']}*
├─ Rating: {analytics['home_rating']:.1f}/100
├─ Form: {analytics.get('home_form', 'N/A')}
├─ Form Analysis: {home_form_analysis}
├─ Goals/Game: {analytics.get('home_stats', {}).get('goals_for', 0) / max(1, analytics.get('home_stats', {}).get('games_played', 1)):.2f}
├─ Goals Against/Game: {analytics.get('home_stats', {}).get('goals_against', 0) / max(1, analytics.get('home_stats', {}).get('games_played', 1)):.2f}
└─ Win Prob: {analytics['home_prob']}%

🔄 *DRAW*
└─ Probability: {analytics['draw_prob']}%

🔴 *{analytics['away_team']}*
├─ Rating: {analytics['away_rating']:.1f}/100
├─ Form: {analytics.get('away_form', 'N/A')}
├─ Form Analysis: {away_form_analysis}
├─ Goals/Game: {analytics.get('away_stats', {}).get('goals_for', 0) / max(1, analytics.get('away_stats', {}).get('games_played', 1)):.2f}
├─ Goals Against/Game: {analytics.get('away_stats', {}).get('goals_against', 0) / max(1, analytics.get('away_stats', {}).get('games_played', 1)):.2f}
└─ Win Prob: {analytics['away_prob']}%

━━━━━━━━━━━━━━━━━━━━━
🎯 *PREDICTION*
├─ Score: {analytics['predicted_score']}
├─ Confidence: {analytics['confidence']}%
└─ Result: {'🏠 Home Win' if analytics['home_prob'] > 50 else '✈️ Away Win' if analytics['away_prob'] > 50 else '🤝 Draw'}

📈 *BET INSIGHT*
{"High confidence bet" if analytics['confidence'] > 20 else "Medium confidence" if analytics['confidence'] > 10 else "Low confidence"} - {analytics['confidence']}% confidence level
"""
        return message
    
    def analyze_form(self, form_string):
        """Analyze form string"""
        if not form_string:
            return "Unknown"
        
        wins = form_string.count('W')
        points = wins * 3 + form_string.count('D')
        max_points = len(form_string) * 3
        
        ratio = points / max_points if max_points > 0 else 0
        
        if ratio > 0.6:
            return "🔥 Excellent Form"
        elif ratio > 0.4:
            return "👍 Good Form"
        elif ratio > 0.2:
            return "📊 Average Form"
        else:
            return "⚠️ Poor Form"
