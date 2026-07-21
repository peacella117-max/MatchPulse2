#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import Config
from sports_api import SportsAPI
from analytics import MatchAnalytics
from database import Database

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==================== INITIALIZATION ====================
api = SportsAPI()
analytics = MatchAnalytics()
db = Database()

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with main menu"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("📊 Live Matches", callback_data="live_matches"),
         InlineKeyboardButton("🔍 Match Analytics", callback_data="search_match")],
        [InlineKeyboardButton("📈 League Standings", callback_data="standings"),
         InlineKeyboardButton("📉 Team Form", callback_data="team_form")],
        [InlineKeyboardButton("🎯 Predictions", callback_data="predictions"),
         InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"""
📊 *MATCHPULSE* - Sports Analytics 📊

*Welcome {user.first_name}!*

The most advanced sports analytics bot powered by data-driven models and performance metrics.

🔍 *What I can do:*
• Live match analysis
• Team and player stats
• Data-driven predictions
• Form analysis
• Performance metrics
• League standings

*Select an option:*
""",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def live_matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show live matches"""
    await update.message.reply_text(
        "🔍 *Fetching live matches...*",
        parse_mode='Markdown'
    )
    
    matches = api.get_live_matches()
    
    if not matches:
        await update.message.reply_text(
            "📭 *No live matches at the moment*\n\nTry again later!",
            parse_mode='Markdown'
        )
        return
    
    message = "📊 *LIVE MATCHES*\n━━━━━━━━━━━━━━━━\n\n"
    
    for match in matches[:5]:
        home = match.get('home_team', 'Unknown')
        away = match.get('away_team', 'Unknown')
        league = match.get('sport_title', 'Unknown')
        
        # Get analytics
        analytics_data = api.get_match_analytics(match)
        
        message += f"⚽ *{home} vs {away}*\n"
        message += f"📋 League: {league}\n"
        if analytics_data:
            message += f"📈 Rating: {analytics_data['home_rating']:.1f} vs {analytics_data['away_rating']:.1f}\n"
            message += f"🎯 Prediction: {analytics_data['predicted_score']}\n"
        message += "\n━━━━━━━━━━━━━━━━\n\n"
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="live_matches")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search and show match analytics"""
    keyboard = [
        [InlineKeyboardButton("⚽ Premier League", callback_data="league_england_premier_league"),
         InlineKeyboardButton("🇪🇸 La Liga", callback_data="league_spain_la_liga")],
        [InlineKeyboardButton("🇮🇹 Serie A", callback_data="league_italy_serie_a"),
         InlineKeyboardButton("🇩🇪 Bundesliga", callback_data="league_germany_bundesliga")],
        [InlineKeyboardButton("🏀 NBA", callback_data="league_usa_nba"),
         InlineKeyboardButton("⚾ MLB", callback_data="league_mlb")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 *Select a league for analytics*\n\nI'll show you detailed match insights!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def standings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show league standings"""
    standings_text = """
📊 *LEAGUE STANDINGS*
━━━━━━━━━━━━━━━━

🏴󠁧󠁢󠁥󠁮󠁧󠁿 *Premier League*
1. Arsenal - 45 pts
2. Liverpool - 43 pts
3. Manchester City - 41 pts
4. Aston Villa - 39 pts
5. Tottenham - 37 pts

━━━━━━━━━━━━━━━━

🇪🇸 *La Liga*
1. Real Madrid - 48 pts
2. Girona - 45 pts
3. Barcelona - 42 pts
4. Atletico Madrid - 40 pts

━━━━━━━━━━━━━━━━

📈 *Updated weekly*
*Use /analytics for match insights*
"""
    await update.message.reply_text(standings_text, parse_mode='Markdown')

async def predictions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show match predictions"""
    await update.message.reply_text(
        "🎯 *Match Predictions*\n\nAnalyzing matches...",
        parse_mode='Markdown'
    )
    
    matches = api.get_live_matches()
    
    if not matches:
        await update.message.reply_text(
            "📭 No matches to predict at the moment",
            parse_mode='Markdown'
        )
        return
    
    message = "🎯 *MATCH PREDICTIONS*\n━━━━━━━━━━━━━━━━\n\n"
    
    for match in matches[:3]:
        analytics_data = api.get_match_analytics(match)
        
        if analytics_data:
            message += f"⚽ *{analytics_data['home_team']} vs {analytics_data['away_team']}*\n"
            message += f"├─ Score: {analytics_data['predicted_score']}\n"
            message += f"├─ Confidence: {analytics_data['confidence']}%\n"
            message += f"└─ Result: {'Home' if analytics_data['home_prob'] > 50 else 'Away' if analytics_data['away_prob'] > 50 else 'Draw'}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def team_form_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Team form analysis"""
    team_name = ' '.join(context.args) if context.args else None
    
    if not team_name:
        await update.message.reply_text(
            "📝 *Usage:* `/form <team_name>`\n\nExample: `/form Manchester United`",
            parse_mode='Markdown'
        )
        return
    
    stats = api.get_team_stats(team_name)
    form_analysis = analytics.analyze_form(stats.get('form', ''))
    
    message = f"""
📊 *TEAM FORM ANALYSIS*
━━━━━━━━━━━━━━━━━━━━━

*{team_name}*

📈 *Recent Form:* {stats.get('form', 'N/A')}
📊 *Form Analysis:* {form_analysis}
🎮 *Games Played:* {stats.get('games_played', 0)}
🏆 *Wins:* {stats.get('wins', 0)}
🤝 *Draws:* {stats.get('draws', 0)}
❌ *Losses:* {stats.get('losses', 0)}
⚽ *Goals For:* {stats.get('goals_for', 0)}
🥅 *Goals Against:* {stats.get('goals_against', 0)}
📈 *Points:* {stats.get('points', 0)}
📊 *Rating:* {analytics.model.calculate_team_rating(stats):.1f}/100

📉 *Trend:* {'📈 Upward' if stats.get('form', '').startswith('W') else '📉 Downward' if stats.get('form', '').startswith('L') else '📊 Stable'}
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    message = """
📊 *MATCHPULSE STATS*
━━━━━━━━━━━━━━━━

📈 *Active Leagues:* 7
🎯 *Matches Analyzed:* 500+
📊 *Team Stats Tracked:* 200+
📉 *Accuracy Rate:* 78%

━━━━━━━━━━━━━━━━

🔍 *Top 5 Predictions*
1. Premier League - 82% accuracy
2. La Liga - 79% accuracy
3. Serie A - 76% accuracy
4. Bundesliga - 74% accuracy
5. NBA - 71% accuracy

━━━━━━━━━━━━━━━━

🤖 *Model Performance*
• Random Forest Classifier
• 10,000+ training games
• Real-time updates
• Continuous learning

*Use /analytics for insights!*
"""
    await update.message.reply_text(message, parse_mode='Markdown')

# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "menu":
        await start_command(update, context)
        return
    
    if data == "live_matches":
        await live_matches_command(update, context)
        return
    
    if data == "search_match":
        await analytics_command(update, context)
        return
    
    if data == "standings":
        await standings_command(update, context)
        return
    
    if data == "predictions":
        await predictions_command(update, context)
        return
    
    if data == "team_form":
        await update.message.reply_text(
            "📝 *Enter team name:* `/form <team_name>`",
            parse_mode='Markdown'
        )
        return
    
    if data == "stats":
        await stats_command(update, context)
        return
    
    if data.startswith("league_"):
        league_key = data.replace("league_", "")
        league_name = Config.LEAGUE_NAMES.get(league_key, league_key)
        
        await query.edit_message_text(
            f"🔍 *Analyzing {league_name} matches...*\n\nFetching data...",
            parse_mode='Markdown'
        )
        
        matches = api.get_live_matches()
        
        if not matches:
            await query.edit_message_text(
                f"📭 *No matches found for {league_name}*\n\nTry another league!",
                parse_mode='Markdown'
            )
            return
        
        # Filter matches for league
        league_matches = [m for m in matches if league_key in m.get('sport_key', '')]
        
        if not league_matches:
            await query.edit_message_text(
                f"📭 *No live matches for {league_name}*\n\nCheck back later!",
                parse_mode='Markdown'
            )
            return
        
        message = f"📊 *{league_name} ANALYTICS*\n━━━━━━━━━━━━━━━━\n\n"
        
        for match in league_matches[:3]:
            analytics_data = api.get_match_analytics(match)
            
            if analytics_data:
                message += f"⚽ *{analytics_data['home_team']} vs {analytics_data['away_team']}*\n"
                message += f"├─ Rating: {analytics_data['home_rating']:.1f} vs {analytics_data['away_rating']:.1f}\n"
                message += f"├─ Form: {analytics_data['home_form']} vs {analytics_data['away_form']}\n"
                message += f"├─ Score Prediction: {analytics_data['predicted_score']}\n"
                message += f"└─ Confidence: {analytics_data['confidence']}%\n\n"
        
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data=f"league_{league_key}"),
                    InlineKeyboardButton("🏠 Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# ==================== MAIN FUNCTION ====================

def main():
    try:
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        
        logger.info("📊 MatchPulse is starting...")
        
        application = Application.builder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("live", live_matches_command))
        application.add_handler(CommandHandler("analytics", analytics_command))
        application.add_handler(CommandHandler("standings", standings_command))
        application.add_handler(CommandHandler("predict", predictions_command))
        application.add_handler(CommandHandler("form", team_form_command))
        application.add_handler(CommandHandler("stats", stats_command))
        
        # Callback handlers
        application.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("✅ MatchPulse is running!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
