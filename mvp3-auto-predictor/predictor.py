# MVP 3: Enhanced Predictor (Uses Real Database)

from db import MatchDatabase
from datetime import datetime, timedelta

class DynamicPredictor:
    def __init__(self, db_path='val_standings.db'):
        self.db = MatchDatabase(db_path)
    
    def predict_match_winner(self, team1, team2):
        # Get all teams with stats and find the specific teams
        all_teams = self.db.get_all_teams_with_stats()
        team1_data = next((team for team in all_teams if team['team'] == team1), None)
        team2_data = next((team for team in all_teams if team['team'] == team2), None)
        
        if not team1_data or not team2_data:
            return {
                'error': 'One or both teams not found',
                'suggestion': 'Check team names and try again'
            }
            
        # Calculate win rates from records
        team1_wins, team1_losses = map(int, team1_data['record'].split('-'))
        team2_wins, team2_losses = map(int, team2_data['record'].split('-'))
        
        team1_matches = team1_wins + team1_losses
        team2_matches = team2_wins + team2_losses
        
        team1_winrate = team1_wins / team1_matches if team1_matches > 0 else 0
        team2_winrate = team2_wins / team2_matches if team2_matches > 0 else 0
        
        # Base prediction on win rates
        total_strength = team1_winrate + team2_winrate
        if total_strength == 0:
            team1_base_prob = 0.5
            team2_base_prob = 0.5
        else:
            team1_base_prob = team1_winrate / total_strength
            team2_base_prob = team2_winrate / total_strength
        
        # Determine predicted winner
        if team1_base_prob > team2_base_prob:
            predicted_winner = team1
            confidence = team1_base_prob
        else:
            predicted_winner = team2
            confidence = team2_base_prob
        
        # Create team records for display
        team1_record = {'wins': team1_wins, 'losses': team1_losses}
        team2_record = {'wins': team2_wins, 'losses': team2_losses}
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_win_rate': team1_winrate,
            'team2_win_rate': team2_winrate,
            'team1_record': team1_record,
            'team2_record': team2_record,
            'team1_match_probability': team1_base_prob,
            'team2_match_probability': team2_base_prob,
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'prediction_date': datetime.now().isoformat()
        }