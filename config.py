import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """MatchPulse Configuration"""
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found")
    
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    
    # API Settings
    ODDS_API_BASE = "https://api.the-odds-api.com/v4"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Leagues
    LEAGUES = [
        'england_premier_league',
        'spain_la_liga',
        'italy_serie_a',
        'germany_bundesliga',
        'france_ligue_one',
        'usa_nba',
        'mlb'
    ]
    
    LEAGUE_NAMES = {
        'england_premier_league': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'spain_la_liga': '🇪🇸 La Liga',
        'italy_serie_a': '🇮🇹 Serie A',
        'germany_bundesliga': '🇩🇪 Bundesliga',
        'france_ligue_one': '🇫🇷 Ligue 1',
        'usa_nba': '🏀 NBA',
        'mlb': '⚾ MLB'
    }
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///matchpulse.db')
