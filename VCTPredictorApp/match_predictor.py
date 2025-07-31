from colorama import Fore, Style, init
init(autoreset=True)
import csv
from difflib import get_close_matches

# Load team data from a CSV file into a dictionary
def load_team_data(csv_file):
    teams = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['team'].strip()  # Get team name and remove extra spaces
            wins = int(row['wins'])     # Convert wins to integer
            losses = int(row['losses']) # Convert losses to integer
            group = row['group'].strip()
            teams[name] = {'wins': wins, 'losses': losses, 'group': group}  # Store in dictionary
    return teams

# Calculate win rate percentage for a team
def get_win_rate(team_data):
    wins = team_data['wins']
    losses = team_data['losses']
    total = wins + losses
    return round(wins / total * 100, 2)  # Return win rate as a percentage

# Calculate prediction confidence based on win rate difference
def predict_confidence(rate1, rate2):
    diff = abs(rate1 - rate2)
    confidence = round(50 + min(diff * 0.75, 50), 2)  # Scale confidence, max 100%
    return confidence

# Find the closest matching team name using fuzzy matching
def fuzzy_lookup(name, teams):
    matches = get_close_matches(name, teams.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None  # Return best match or None

# Predict which team is more likely to win and print results
def predict(team1, team2, teams):
    data1 = teams[team1]
    data2 = teams[team2]
    rate1 = get_win_rate(data1)
    rate2 = get_win_rate(data2)

    print(f"\n{team1} (Group {data1['group']}): {rate1}% win rate")
    print(f"{team2} (Group {data2['group']}): {rate2}% win rate")

    if rate1 > rate2:
        predicted = team1
    elif rate2 > rate1:
        predicted = team2
    else:
        print("\nPrediction: Equal win rate, could go either way. :)")  # Equal win rates
        return

    confidence = predict_confidence(rate1, rate2)
    print(f"\nPrediction: {Fore.GREEN}{predicted} is more likely to win.{Style.RESET_ALL}")
    print(f"Confidence level: {Fore.YELLOW}{confidence}%{Style.RESET_ALL}")

def list_teams_by_group(teams):
    grouped = {}
    for team, data in teams.items():
        group = data['group']
        grouped.setdefault(group, []).append(team)

    print("\nAvailable teams by group:")
    for group in sorted(grouped.keys()):
        print(f"  Group {group}: {', '.join(sorted(grouped[group]))}")

# Main function to run the predictor
def main():
    print("=== VCT Americas Match Predictor v1.5 ===")
    teams = load_team_data("team_records.csv")  # Load team data
    list_teams_by_group(teams)

    # Get user input for both teams
    team1_input = input("Enter Team 1: ").strip()
    team2_input = input("Enter Team 2: ").strip()

    # Prevent comparing the same team
    if team1_input.lower() == team2_input.lower():
        print("Error: Cannot compare a team to itself.")
        return

    # Try to find the closest matching team names
    team1 = fuzzy_lookup(team1_input, teams)
    team2 = fuzzy_lookup(team2_input, teams)
    print(f"Matched input to: {team1} vs {team2}")


    # If either team is not found, show error and available teams
    if not team1 or not team2:
        print("Error: One or both team names not recognized.")
        print("Available teams:", ", ".join(sorted(teams.keys())))        
        return

    # Make and display the prediction
    predict(team1, team2, teams)

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()