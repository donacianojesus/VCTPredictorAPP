#!/usr/bin/env python3
"""
VCT Predictor Routes
All web endpoints and API calls
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import os
import json

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/api/health')
def api_health():
    """API endpoint to get scraper health status"""
    try:
        # Get health status from database
        health_data = current_app.db.get_scraper_health()
        
        # Calculate success rate
        success_rate = 0
        if health_data['total_runs'] > 0:
            success_rate = (health_data['success_count'] / health_data['total_runs']) * 100
        
        return jsonify({
            'status': health_data['status'],
            'message': 'Health data from database',
            'last_run': health_data['last_run'].isoformat() if health_data['last_run'] else None,
            'success_count': health_data['success_count'],
            'total_runs': health_data['total_runs'],
            'success_rate': round(success_rate, 1)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to load health data: {str(e)}',
            'last_run': None,
            'success_count': 0,
            'total_runs': 0,
            'success_rate': 0
        }), 500

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """Main page with team selection and predictions"""
    # Get all teams with their stats and group info
    teams_with_stats = current_app.db.get_all_teams_with_stats()
    
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
                    prediction = current_app.predictor.predict_match_winner(selected_team1, selected_team2)
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
