from flask import Flask, render_template, request
import csv
import os

# Initialize Flask app
app = Flask(__name__)

def load_team_records():
    """Load team records from CSV file and organize by groups"""
    team_records = {}
    teams_by_group = {"A": [], "B": []}
    
    # Path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'VCTPredictorApp', 'team_records.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                team_name = row['team'].lower().strip()
                wins = int(row['wins'])
                losses = int(row['losses'])
                group = row['group']
                
                # Store team record
                team_records[team_name] = {
                    "wins": wins,
                    "losses": losses,
                    "group": group
                }
                
                # Add to group list
                if group in teams_by_group:
                    teams_by_group[group].append({
                        "name": row['team'],
                        "wins": wins,
                        "losses": losses,
                        "win_rate": wins / (wins + losses) if (wins + losses) > 0 else 0
                    })
        
        # Sort teams within each group by win rate (descending)
        for group in teams_by_group:
            teams_by_group[group].sort(key=lambda x: x['win_rate'], reverse=True)
            
    except FileNotFoundError:
        print(f"Warning: Could not find {csv_path}")
        # Fallback to hardcoded data if CSV not found
        team_records = {
            "cloud9": {"wins": 2, "losses": 1, "group": "A"},
            "sentinels": {"wins": 3, "losses": 0, "group": "A"},
            "g2 esports": {"wins": 2, "losses": 1, "group": "A"},
            "evil geniuses": {"wins": 1, "losses": 2, "group": "A"},
            "2game esports": {"wins": 1, "losses": 2, "group": "A"},
            "furia": {"wins": 0, "losses": 3, "group": "A"},
            "100 thieves": {"wins": 2, "losses": 1, "group": "B"},
            "leviatan": {"wins": 1, "losses": 2, "group": "B"},
            "nrg": {"wins": 2, "losses": 1, "group": "B"},
            "kru esports": {"wins": 2, "losses": 1, "group": "B"},
            "loud": {"wins": 1, "losses": 2, "group": "B"},
            "mibr": {"wins": 1, "losses": 2, "group": "B"}
        }
        
        # Organize fallback data by groups
        for team_name, record in team_records.items():
            group = record["group"]
            if group in teams_by_group:
                teams_by_group[group].append({
                    "name": team_name.title(),
                    "wins": record["wins"],
                    "losses": record["losses"],
                    "win_rate": record["wins"] / (record["wins"] + record["losses"]) if (record["wins"] + record["losses"]) > 0 else 0
                })
        
        for group in teams_by_group:
            teams_by_group[group].sort(key=lambda x: x['win_rate'], reverse=True)
    
    return team_records, teams_by_group

# Load team data
TEAM_RECORDS, TEAMS_BY_GROUP = load_team_records()

def get_team_win_rate(team_name):
    """Same logic as MVP 1"""
    team_name = team_name.lower().strip()
    
    if team_name not in TEAM_RECORDS:
        return None
    
    record = TEAM_RECORDS[team_name]
    total_games = record["wins"] + record["losses"]
    
    if total_games == 0:
        return 0.5
    
    return record["wins"] / total_games

def predict_match_winner(team1, team2):
    """Same logic as MVP 1, but optimized for web display"""
    
    team1_win_rate = get_team_win_rate(team1)
    team2_win_rate = get_team_win_rate(team2)
    
    if team1_win_rate is None or team2_win_rate is None:
        return None
    
    # Calculate match probabilities
    total_strength = team1_win_rate + team2_win_rate
    team1_match_probability = team1_win_rate / total_strength
    team2_match_probability = team2_win_rate / total_strength
    
    # Determine winner
    if team1_match_probability > team2_match_probability:
        predicted_winner = team1
        confidence = team1_match_probability
    else:
        predicted_winner = team2
        confidence = team2_match_probability
    
    return {
        "team1": team1,
        "team2": team2,
        "team1_record": TEAM_RECORDS[team1.lower()],
        "team2_record": TEAM_RECORDS[team2.lower()],
        "team1_win_rate": team1_win_rate,
        "team2_win_rate": team2_win_rate,
        "team1_match_probability": team1_match_probability,
        "team2_match_probability": team2_match_probability,
        "predicted_winner": predicted_winner,
        "confidence": confidence
    }

def get_team_list():
    """Get list of teams for dropdowns, organized by groups"""
    return TEAMS_BY_GROUP

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main page - handles both displaying the form and processing predictions
    My reasoning: Keep it simple with one route that does everything
    """
    
    # Get team list for dropdowns (organized by groups)
    teams_by_group = get_team_list()
    
    # Initialize variables
    prediction = None
    error_message = None
    selected_team1 = ""
    selected_team2 = ""
    
    # Handle form submission
    if request.method == 'POST':
        team1 = request.form.get('team1', '').strip()
        team2 = request.form.get('team2', '').strip()
        
        # Remember selections for the form
        selected_team1 = team1
        selected_team2 = team2
        
        # Validate input
        if not team1 or not team2:
            error_message = "Please select both teams."
        elif team1 == team2:
            error_message = "Please select two different teams."
        else:
            # Make prediction
            prediction = predict_match_winner(team1, team2)
            if prediction is None:
                error_message = "Error making prediction. Please try again."
    
    # Render the page (same template for GET and POST)
    return render_template('index.html', 
                         teams_by_group=teams_by_group,
                         prediction=prediction,
                         error_message=error_message,
                         selected_team1=selected_team1,
                         selected_team2=selected_team2)

if __name__ == '__main__':
    print("Starting VCT Match Predictor Web App...")
    print("Open your browser to: http://localhost:5000")
    print("Or http://127.0.0.1:5000/ on macOS")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(debug=True, host='localhost', port=5000)