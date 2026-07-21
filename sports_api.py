import requests
import time
from datetime import datetime, timedelta
from cachetools import cached, TTLCache
from config import Config

cache = TTLCache(maxsize=200, ttl=Config.CACHE_TIMEOUT)

class SportsAPI:
    """Sports data API handler"""
    
    def __init__(self):
        self.api_key = Config.ODDS_API_KEY
        self.base_url = Config.ODDS_API_BASE
        self.session = requests.Session()
    
    @cached(cache)
    def get_live_matches(self, sport='soccer'):
        """Get live matches"""
        try:
            url = f"{self.base_url}/sports/{sport}/odds"
            params = {
                'apiKey': self.api_key,
                'region': 'eu',
                'markets': 'h2h',
                'dateFormat': 'iso'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 429:
                time.sleep(5)
                response = self.session.get(url, params=params, timeout=15)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return []
    
    def get_match_analytics(self, match_data):
        """Generate analytics for a match"""
        try:
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            # Get team stats from database or generate synthetic data
            home_stats = self.get_team_stats(home_team)
            away_stats = self.get_team_stats(away_team)
            
            # Calculate metrics
            home_attack = home_stats.get('goals_for', 0) / max(1, home_stats.get('games_played', 1))
            away_attack = away_stats.get('goals_for', 0) / max(1, away_stats.get('games_played', 1))
            home_defense = home_stats.get('goals_against', 0) / max(1, home_stats.get('games_played', 1))
            away_defense = away_stats.get('goals_against', 0) / max(1, away_stats.get('games_played', 1))
            
            # Calculate ratings
            home_rating = (home_attack * 2 + (1 - home_defense)) * 50
            away_rating = (away_attack * 2 + (1 - away_defense)) * 50
            
            # Predict match outcome
            home_prob = home_rating / (home_rating + away_rating) * 100
            away_prob = away_rating / (home_rating + away_rating) * 100
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_rating': round(home_rating, 1),
                'away_rating': round(away_rating, 1),
                'home_prob': round(home_prob, 1),
                'away_prob': round(away_prob, 1),
                'draw_prob': round(100 - home_prob - away_prob, 1),
                'home_form': home_stats.get('form', 'LDW'),
                'away_form': away_stats.get('form', 'DLW'),
                'predicted_score': f"{int(home_prob/25)}-{int(away_prob/25)}",
                'confidence': round(abs(home_prob - away_prob) / 2, 1)
            }
        except Exception as e:
            print(f"Analytics error: {e}")
            return None
    
    def get_team_stats(self, team_name):
        """Get team statistics"""
        # In production, this would query a real database
        # For demo, return synthetic data
        import random
        return {
            'games_played': random.randint(10, 30),
            'goals_for': random.randint(15, 60),
            'goals_against': random.randint(10, 40),
            'form': ''.join(random.choice(['W', 'D', 'L']) for _ in range(5)),
            'points': random.randint(20, 70)
        }
    
    def analyze_form(self, form_string):
        """Analyze team form string"""
        if not form_string:
            return "Unknown"
        
        wins = form_string.count('W')
        draws = form_string.count('D')
        losses = form_string.count('L')
        
        points = wins * 3 + draws
        max_points = len(form_string) * 3
        
        if points / max_points > 0.6:
            return "Excellent"
        elif points / max_points > 0.4:
            return "Good"
        elif points / max_points > 0.2:
            return "Average"
        else:
            return "Poor"
    
    def format_analytics(self, analytics):
        """Format analytics for display"""
        if not analytics:
            return "No analytics available"
        
        home_emoji = '🟢' if analytics['home_rating'] > analytics['away_rating'] else '🟡'
        away_emoji = '🟢' if analytics['away_rating'] > analytics['home_rating'] else '🟡'
        
        message = f"""
📊 *MATCH ANALYTICS*
━━━━━━━━━━━━━━━━━━━━━

🔵 *{analytics['home_team']}* {home_emoji}
├─ Rating: {analytics['home_rating']:.1f}
├─ Form: {analytics['home_form']} ({self.analyze_form(analytics['home_form'])})
└─ Win Prob: {analytics['home_prob']}%

⚪ *Draw*
└─ Probability: {analytics['draw_prob']}%

🔴 *{analytics['away_team']}* {away_emoji}
├─ Rating: {analytics['away_rating']:.1f}
├─ Form: {analytics['away_form']} ({self.analyze_form(analytics['away_form'])})
└─ Win Prob: {analytics['away_prob']}%

━━━━━━━━━━━━━━━━━━━━━
🎯 *PREDICTION*
├─ Score: {analytics['predicted_score']}
├─ Confidence: {analytics['confidence']}%
└─ Result: {'Home Win' if analytics['home_prob'] > 50 else 'Away Win' if analytics['away_prob'] > 50 else 'Draw'}
"""
        return message
