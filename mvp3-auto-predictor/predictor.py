# MVP 3: Enhanced Predictor (Uses Real Database)

from db import MatchDatabase
from datetime import datetime, timedelta

class DynamicPredictor:
    def __init__(self, db_path='val_standings.db'):
        self.db = MatchDatabase(db_path)
    
    def predict_match_winner(self, team1, team2):
        team1_data = self.db._get_team_data(team1)
        team2_data = self.db._get_team_data(team2)
        
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
        
        # Adjust based on head-to-head if we have data
        h2h_data = self.db.get_head_to_head(team1, team2, limit=5)
        if h2h_data['total_matches'] >= 2:  # Only adjust if we have meaningful H2H data
            h2h_weight = min(0.3, h2h_data['total_matches'] * 0.1)  # Max 30% influence
            
            team1_h2h_prob = h2h_data['team1_win_rate']
            team2_h2h_prob = 1 - team1_h2h_prob
            
            # Weighted average of base probability and H2H
            team1_match_prob = (team1_base_prob * (1 - h2h_weight)) + (team1_h2h_prob * h2h_weight)
            team2_match_prob = (team2_base_prob * (1 - h2h_weight)) + (team2_h2h_prob * h2h_weight)
        else:
            team1_match_prob = team1_base_prob
            team2_match_prob = team2_base_prob
        
        # Determine predicted winner
        if team1_match_prob > team2_match_prob:
            predicted_winner = team1
            confidence = team1_match_prob
        else:
            predicted_winner = team2
            confidence = team2_match_prob
        
        # Calculate prediction strength based on data quality
        data_confidence = self._calculate_data_confidence(team1_data, team2_data, h2h_data)
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_stats': team1_data,
            'team2_stats': team2_data,
            'head_to_head': h2h_data,
            'team1_match_probability': team1_match_prob,
            'team2_match_probability': team2_match_prob,
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'data_confidence': data_confidence,
            'prediction_date': datetime.now().isoformat(),
            'days_analyzed': 30
        }
    
    def _calculate_data_confidence(self, team1_stats, team2_stats, h2h_data):
        """
        Calculate how confident we should be in our prediction based on data quality
        My reasoning: More matches = better prediction, recent data = better prediction
        """
        
        # Factor 1: Number of recent matches for each team
        team1_matches = team1_stats['matches_found']
        team2_matches = team2_stats['matches_found']
        
        min_matches = min(team1_matches, team2_matches)
        match_confidence = min(1.0, min_matches / 10)  # Max confidence at 10+ matches each
        
        # Factor 2: How recent is the data
        try:
            team1_last_match = datetime.fromisoformat(team1_stats['last_updated'])
            team2_last_match = datetime.fromisoformat(team2_stats['last_updated'])
            
            days_since_team1 = (datetime.now() - team1_last_match).days
            days_since_team2 = (datetime.now() - team2_last_match).days
            
            max_days_old = max(days_since_team1, days_since_team2)
            recency_confidence = max(0.1, 1.0 - (max_days_old / 30))  # Declines over 30 days
        except:
            recency_confidence = 0.5
        
        # Factor 3: Head-to-head data availability
        h2h_confidence = min(1.0, h2h_data['total_matches'] / 5) if h2h_data['total_matches'] > 0 else 0
        
        # Combined confidence score
        overall_confidence = (match_confidence * 0.5 + recency_confidence * 0.3 + h2h_confidence * 0.2)
        
        return {
            'overall': overall_confidence,
            'match_data_quality': match_confidence,
            'data_recency': recency_confidence,
            'head_to_head_data': h2h_confidence,
            'interpretation': self._interpret_data_confidence(overall_confidence)
        }
    
    def _interpret_data_confidence(self, confidence):
        """Human-readable interpretation of data confidence"""
        if confidence >= 0.8:
            return "High - Lots of recent match data available"
        elif confidence >= 0.6:
            return "Good - Sufficient recent data for reliable prediction"
        elif confidence >= 0.4:
            return "Moderate - Limited recent data, prediction less reliable"
        elif confidence >= 0.2:
            return "Low - Very limited recent data available"
        else:
            return "Very Low - Minimal data, prediction highly uncertain"
    
    def get_team_form_summary(self, team_name, days_back=30):
        """
        Get a human-readable summary of team's recent form
        My reasoning: Users want to understand WHY the prediction was made
        """
        stats = self.db.calculate_team_stats(team_name, days_back)
        recent_matches = self.db.get_team_recent_matches(team_name, days_back, limit=5)
        
        if stats['matches_found'] == 0:
            return f"No recent match data found for {team_name}"
        
        # Recent trend (last 5 matches)
        if recent_matches:
            recent_wins = 0
            for match in recent_matches[:5]:
                # Determine if team won this match
                if match['team1'].lower() == team_name.lower():
                    if match['team1_score'] > match['team2_score']:
                        recent_wins += 1
                else:
                    if match['team2_score'] > match['team1_score']:
                        recent_wins += 1
            
            recent_form = f"{recent_wins}W-{len(recent_matches[:5]) - recent_wins}L"
        else:
            recent_form = "No recent matches"
        
        # Form trend
        if stats['win_rate'] > 0.7:
            form_desc = "Excellent form"
        elif stats['win_rate'] > 0.6:
            form_desc = "Good form"
        elif stats['win_rate'] > 0.4:
            form_desc = "Average form"
        else:
            form_desc = "Poor form"
        
        return {
            'team_name': team_name,
            'overall_record': f"{stats['wins']}W-{stats['losses']}L",
            'win_rate': f"{stats['win_rate']:.1%}",
            'recent_form': recent_form,
            'form_description': form_desc,
            'matches_analyzed': stats['matches_found'],
            'last_match': stats['last_updated'],
            'average_score': f"{stats['avg_score']:.1f}"
        }
    
    def compare_teams(self, team1, team2, days_back=30):
        """
        Side-by-side comparison of two teams
        My reasoning: Make it easy to see why one team is favored
        """
        team1_form = self.get_team_form_summary(team1, days_back)
        team2_form = self.get_team_form_summary(team2, days_back)
        h2h = self.db.get_head_to_head(team1, team2)
        
        comparison = {
            'team1_form': team1_form,
            'team2_form': team2_form,
            'head_to_head': {
                'total_matches': h2h['total_matches'],
                'team1_wins': h2h['team1_wins'],
                'team2_wins': h2h['team2_wins'],
                'team1_h2h_rate': f"{h2h['team1_win_rate']:.1%}" if h2h['total_matches'] > 0 else "No data"
            },
            'key_differences': []
        }
        
        # Identify key differences
        if isinstance(team1_form, dict) and isinstance(team2_form, dict):
            team1_wr = float(team1_form['win_rate'].replace('%', '')) / 100
            team2_wr = float(team2_form['win_rate'].replace('%', '')) / 100
            
            if abs(team1_wr - team2_wr) > 0.15:
                if team1_wr > team2_wr:
                    comparison['key_differences'].append(f"{team1} has significantly better recent win rate")
                else:
                    comparison['key_differences'].append(f"{team2} has significantly better recent win rate")
            
            if team1_form['matches_analyzed'] < 5:
                comparison['key_differences'].append(f"{team1} has very limited recent match data")
            if team2_form['matches_analyzed'] < 5:
                comparison['key_differences'].append(f"{team2} has very limited recent match data")
        
        return comparison
    
    def get_available_teams(self):
        """Get list of teams with recent match data for dropdowns"""
        return self.db.get_available_teams()
    
    def get_prediction_explanation(self, prediction_result):
        """
        Generate human-readable explanation of the prediction
        My reasoning: Users should understand the 'why' behind predictions
        """
        if 'error' in prediction_result:
            return prediction_result['error']
        
        team1 = prediction_result['team1']
        team2 = prediction_result['team2']
        winner = prediction_result['predicted_winner']
        confidence = prediction_result['confidence']
        
        team1_stats = prediction_result['team1_stats']
        team2_stats = prediction_result['team2_stats']
        h2h = prediction_result['head_to_head']
        
        explanation = []
        
        # Overall prediction
        explanation.append(f"**Prediction: {winner} wins with {confidence:.1%} confidence**")
        explanation.append("")
        
        # Team performance comparison
        explanation.append("**Recent Performance:**")
        explanation.append(f"• {team1}: {team1_stats['wins']}W-{team1_stats['losses']}L ({team1_stats['win_rate']:.1%}) in last {team1_stats['matches_found']} matches")
        explanation.append(f"• {team2}: {team2_stats['wins']}W-{team2_stats['losses']}L ({team2_stats['win_rate']:.1%}) in last {team2_stats['matches_found']} matches")
        explanation.append("")
        
        # Head-to-head
        if h2h['total_matches'] > 0:
            explanation.append("**Head-to-Head Record:**")
            explanation.append(f"• {team1} vs {team2}: {h2h['team1_wins']}-{h2h['team2_wins']} (last {h2h['total_matches']} matches)")
            if h2h['total_matches'] >= 2:
                explanation.append(f"• {team1} wins {h2h['team1_win_rate']:.1%} of recent matchups")
        else:
            explanation.append("**Head-to-Head:** No recent matches between these teams")
        
        explanation.append("")
        
        # Data quality
        data_conf = prediction_result['data_confidence']
        explanation.append(f"**Prediction Reliability:** {data_conf['interpretation']}")
        
        return "\n".join(explanation)

# Make sure the class is available for import
__all__ = ['DynamicPredictor']

# Usage example and testing
if __name__ == "__main__":
    # Test the enhanced predictor
    print("Testing Dynamic Predictor with database...")
    
    predictor = DynamicPredictor()
    
    # Test prediction
    result = predictor.predict_match_winner("Sentinels", "100 Thieves")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        print(f"Suggestion: {result['suggestion']}")
    else:
        print(f"\nPrediction: {result['predicted_winner']} wins")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Data quality: {result['data_confidence']['interpretation']}")
        
        # Show explanation
        explanation = predictor.get_prediction_explanation(result)
        print(f"\nDetailed Explanation:")
        print(explanation)
    
    # Test team comparison
    print(f"\n" + "="*50)
    print("Team Comparison Test:")
    comparison = predictor.compare_teams("Sentinels", "LOUD")
    
    if isinstance(comparison['team1_form'], dict):
        print(f"Sentinels: {comparison['team1_form']['overall_record']} ({comparison['team1_form']['win_rate']})")
    if isinstance(comparison['team2_form'], dict):
        print(f"LOUD: {comparison['team2_form']['overall_record']} ({comparison['team2_form']['win_rate']})")
    
    # Show available teams
    teams = predictor.get_available_teams()
    print(f"\nAvailable teams: {len(teams)}")
    print(f"Sample: {teams[:5]}")