from predictor import DynamicPredictor
from flask import Flask, render_template, request
from db import MatchDatabase
from datetime import datetime
import os

app = Flask(__name__)

# Get absolute path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "val_standings.db")

# Initialize DB and predictor once with absolute path
db = MatchDatabase(DB_PATH)
predictor = DynamicPredictor(DB_PATH)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Get all teams with their stats and group info
    teams_with_stats = db.get_all_teams_with_stats()
    
    # Organize teams by group for display
    teams_by_group = {'Alpha': [], 'Omega': []}
    for team in teams_with_stats:
        if team['group_name'] in teams_by_group:
            teams_by_group[team['group_name']].append({
                'name': team['team'],
                'record': team['record'],
                'map_diff': team['map_diff'],
                'round_diff': team['round_diff'],
                'delta': team['delta']
            })
    
    selected_team1 = None
    selected_team2 = None
    prediction = None
    error_message = None
    
    if request.method == 'POST':
        selected_team1 = request.form.get('team1')
        selected_team2 = request.form.get('team2')
        
        if not selected_team1 or not selected_team2:
            error_message = "Please select two teams."
        elif selected_team1 == selected_team2:
            error_message = "Please select two different teams."
        else:
            # Validate both teams exist and belong to the same group
            team1_data = next((t for t in teams_with_stats if t['team'] == selected_team1), None)
            team2_data = next((t for t in teams_with_stats if t['team'] == selected_team2), None)
            
            if not team1_data or not team2_data:
                error_message = "One or both selected teams are invalid."
            elif team1_data['group_name'] != team2_data['group_name']:
                error_message = "Teams must be from the same group."
            else:
                try:
                    prediction = predictor.predict_match_winner(selected_team1, selected_team2)
                    if 'error' in prediction:
                        error_message = prediction['error']
                except Exception as e:
                    error_message = f"Prediction failed: {str(e)}"
    
    return render_template(
        'index.html',
        teams_by_group=teams_by_group,
        selected_team1=selected_team1,
        selected_team2=selected_team2,
        prediction=prediction,
        error_message=error_message,
        last_updated=datetime.fromisoformat(max(team['last_updated'] for team in teams_with_stats)) if teams_with_stats else None
    )

if __name__ == "__main__":
    app.run(debug=True)
