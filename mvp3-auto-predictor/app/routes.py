#!/usr/bin/env python3
"""
VCT Predictor Routes
All web endpoints and API calls
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import os
import json
import threading
import time
from bs4 import BeautifulSoup

# Create blueprint
main_bp = Blueprint('main', __name__)

def check_db_available():
    """Check if database is available"""
    if not current_app.db:
        return False, "Database not available"
    return True, "Database available"

def run_auto_scraper():
    """Run the scraper in a background thread"""
    try:
        if current_app.db and current_app.predictor:
            from app.services.scraper import VCTScraper
            
            # Create scraper instance
            scraper = VCTScraper()
            
            # Run the scrape
            success = scraper.run_scrape()
            
            if success:
                print("✅ Auto-scraper completed successfully")
            else:
                print("❌ Auto-scraper failed")
                
    except Exception as e:
        print(f"❌ Auto-scraper error: {e}")

@main_bp.route('/api/health')
def api_health():
    """API endpoint to get scraper health status"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'status': 'error',
                'message': message,
                'last_run': None,
                'success_count': 0,
                'total_runs': 0,
                'success_rate': 0
            }), 503
        
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

@main_bp.route('/api/run-scraper', methods=['GET', 'POST'])
def run_scraper():
    """Run the scraper manually"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Check if scraper is available
        if not hasattr(current_app, 'scraper_service'):
            from app.services.scraper import VCTScraper
            current_app.scraper_service = VCTScraper()
        
        # Run the scraper
        success = current_app.scraper_service.run_scrape()
        
        if success:
            # Get updated team count
            try:
                teams_with_stats = current_app.db.get_all_teams_with_stats()
                teams_count = len(teams_with_stats) if teams_with_stats else 0
            except:
                teams_count = 0
            
            return jsonify({
                'success': True,
                'message': 'Scraper completed successfully',
                'teams_count': teams_count
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Scraper failed to complete'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/init-db')
def init_database():
    """Initialize database with sample data (for Railway deployment)"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Sample team data for VCT Americas
        sample_teams = [
            # Group Alpha
            {'group_name': 'Alpha', 'team': 'Sentinels', 'record': '4-1', 'map_diff': '8/2', 'round_diff': '104/78', 'delta': 26.0},
            {'group_name': 'Alpha', 'team': 'LOUD', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '98/82', 'delta': 16.0},
            {'group_name': 'Alpha', 'team': '100 Thieves', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '92/88', 'delta': 4.0},
            {'group_name': 'Alpha', 'team': 'NRG', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '86/94', 'delta': -8.0},
            {'group_name': 'Alpha', 'team': 'Cloud9', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '84/96', 'delta': -12.0},
            {'group_name': 'Alpha', 'team': 'MIBR', 'record': '1-4', 'map_diff': '2/8', 'round_diff': '76/104', 'delta': -28.0},
            
            # Group Omega
            {'group_name': 'Omega', 'team': 'Leviatán', 'record': '4-1', 'map_diff': '8/2', 'round_diff': '102/76', 'delta': 26.0},
            {'group_name': 'Omega', 'team': 'KRÜ', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '96/84', 'delta': 12.0},
            {'group_name': 'Omega', 'team': 'FURIA', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '94/86', 'delta': 8.0},
            {'group_name': 'Omega', 'team': 'Evil Geniuses', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '88/92', 'delta': -4.0},
            {'group_name': 'Omega', 'team': 'G2 Esports', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '86/94', 'delta': -8.0},
            {'group_name': 'Omega', 'team': 'Shopify Rebellion', 'record': '1-4', 'map_diff': '2/8', 'round_diff': '78/102', 'delta': -24.0}
        ]
        
        # Insert sample teams
        for team_data in sample_teams:
            current_app.db.insert_match_data(
                group=team_data['group_name'],
                team=team_data['team'],
                record=team_data['record'],
                map_diff=team_data['map_diff'],
                round_diff=team_data['round_diff'],
                delta=team_data['delta']
            )
        
        # Initialize scraper health
        current_app.db.update_scraper_health(
            status='idle',
            success_count=0,
            total_runs=0
        )
        
        # Verify data
        teams = current_app.db.get_all_teams_with_stats()
        
        return jsonify({
            'success': True,
            'message': f'Database initialized with {len(teams)} teams',
            'teams_count': len(teams),
            'scraper_status': 'idle'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/debug-scraper')
def debug_scraper():
    """Debug endpoint to test scraper and find working VCT URLs"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Check if scraper is available
        if not hasattr(current_app, 'scraper_service'):
            from app.services.scraper import VCTScraper
            current_app.scraper_service = VCTScraper()
        
        # Test different VCT URLs
        test_urls = [
            "https://www.vlr.gg/event/standings/2025-americas-stage-2",
            "https://www.vlr.gg/event/standings/2025-americas-stage-1",
            "https://www.vlr.gg/event/standings/2024-americas-stage-2",
            "https://www.vlr.gg/event/standings/2024-americas-stage-1"
        ]
        
        results = []
        for url in test_urls:
            try:
                response = current_app.scraper_service.scraper.get(url, timeout=10)
                status = response.status_code
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    standings_table = (
                        soup.find('table', class_='wf-table') or
                        soup.find('table', class_='standings-table') or
                        soup.find('table', class_='event-standings-table') or
                        soup.find('table')
                    )
                    has_table = standings_table is not None
                    results.append({
                        'url': url,
                        'status': status,
                        'has_table': has_table,
                        'working': has_table
                    })
                else:
                    results.append({
                        'url': url,
                        'status': status,
                        'has_table': False,
                        'working': False
                    })
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'has_table': False,
                    'working': False,
                    'error': str(e)
                })
        
        # Try to find working VCT 2025 URLs
        try:
            working_urls = current_app.scraper_service.find_vct_2025_urls()
            url_search_success = True
            found_urls = working_urls
        except Exception as e:
            url_search_success = False
            found_urls = []
            url_search_error = str(e)
        
        # Try to run a test scrape
        try:
            test_scrape = current_app.scraper_service.scrape_vct_standings()
            scrape_success = test_scrape is not False
            teams_count = len(test_scrape) if test_scrape else 0
        except Exception as e:
            scrape_success = False
            teams_count = 0
            scrape_error = str(e)
        
        # Inspect a working page if available
        page_inspection = None
        page_analysis = None
        if found_urls:
            try:
                # First do basic page inspection
                page_inspection = current_app.scraper_service.inspect_vct_page(found_urls[0])
                if page_inspection:
                    page_inspection = "Page inspection completed successfully"
                else:
                    page_inspection = "Page inspection failed"
                
                # Then do detailed page structure analysis
                page_analysis = current_app.scraper_service.analyze_vct_page_structure(found_urls[0])
                if page_analysis:
                    page_analysis = "Page structure analysis completed successfully"
                else:
                    page_analysis = "Page structure analysis failed"
                    
            except Exception as e:
                page_inspection = f"Page inspection error: {str(e)}"
                page_analysis = f"Page analysis error: {str(e)}"
        
        return jsonify({
            'success': True,
            'url_tests': results,
            'url_search': {
                'success': url_search_success,
                'found_urls': found_urls,
                'error': url_search_error if 'url_search_error' in locals() else None
            },
            'scrape_test': {
                'success': scrape_success,
                'teams_count': teams_count,
                'error': scrape_error if 'scrape_error' in locals() else None
            },
            'page_inspection': page_inspection,
            'page_analysis': page_analysis,
            'message': 'Debug information collected'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/test-scraper-detailed')
def test_scraper_detailed():
    """Detailed scraper test endpoint that shows all the debugging information"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Check if scraper is available
        if not hasattr(current_app, 'scraper_service'):
            from app.services.scraper import VCTScraper
            current_app.scraper_service = VCTScraper()
        
        # Get the main VCT 2025 URL
        vct_url = "https://www.vlr.gg/event/2501/vct-2025-americas-stage-2"
        
        # Do detailed page analysis
        analysis_results = {}
        
        try:
            # Analyze page structure
            soup = current_app.scraper_service.analyze_vct_page_structure(vct_url)
            if soup:
                # Extract specific information
                page_text = soup.get_text()
                
                # Count group mentions
                analysis_results['alpha_count'] = page_text.lower().count('alpha')
                analysis_results['omega_count'] = page_text.lower().count('omega')
                analysis_results['group_a_count'] = page_text.lower().count('group a')
                analysis_results['group_b_count'] = page_text.lower().count('group b')
                
                # Count tables
                all_tables = soup.find_all('table')
                analysis_results['total_tables'] = len(all_tables)
                
                # Look for team names
                team_indicators = ['sentinels', 'loud', '100 thieves', 'nrg', 'cloud9', 'mibr', 'leviatán', 'krü', 'furia', 'evil geniuses', 'g2 esports', 'shopify rebellion']
                found_teams = []
                for team in team_indicators:
                    if team.lower() in page_text.lower():
                        found_teams.append(team)
                analysis_results['found_teams'] = found_teams
                
                # Look for standings table
                standings_table = (
                    soup.find('table', class_='wf-table') or
                    soup.find('table', class_='standings-table') or
                    soup.find('table', class_='event-standings-table') or
                    soup.find('table')
                )
                
                if standings_table:
                    rows = standings_table.find_all('tr')
                    analysis_results['standings_table_rows'] = len(rows)
                    analysis_results['standings_table_found'] = True
                    
                    # Show first few rows structure
                    if len(rows) > 1:
                        first_row = rows[0]
                        cells = first_row.find_all(['th', 'td'])
                        headers = [cell.get_text(strip=True) for cell in cells]
                        analysis_results['table_headers'] = headers
                        
                        # Show sample data from first few rows
                        sample_rows = []
                        for i in range(min(3, len(rows))):
                            row_cells = rows[i].find_all('td')
                            row_text = [cell.get_text(strip=True) for cell in row_cells]
                            sample_rows.append(row_text)
                        analysis_results['sample_rows'] = sample_rows
                else:
                    analysis_results['standings_table_found'] = False
                
                analysis_results['analysis_success'] = True
            else:
                analysis_results['analysis_success'] = False
                analysis_results['error'] = 'Failed to analyze page structure'
                
        except Exception as e:
            analysis_results['analysis_success'] = False
            analysis_results['error'] = str(e)
        
        # Try to run the scraper
        try:
            teams_data = current_app.scraper_service.scrape_vct_standings()
            if teams_data:
                analysis_results['scrape_success'] = True
                analysis_results['teams_count'] = len(teams_data)
                
                # Group distribution
                alpha_teams = [t for t in teams_data if t['group_name'] == 'Alpha']
                omega_teams = [t for t in teams_data if t['group_name'] == 'Omega']
                analysis_results['alpha_count'] = len(alpha_teams)
                analysis_results['omega_count'] = len(omega_teams)
                analysis_results['teams_data'] = teams_data
            else:
                analysis_results['scrape_success'] = False
                analysis_results['teams_count'] = 0
                
        except Exception as e:
            analysis_results['scrape_success'] = False
            analysis_results['scrape_error'] = str(e)
        
        return jsonify({
            'success': True,
            'url_tested': vct_url,
            'analysis_results': analysis_results,
            'message': 'Detailed scraper analysis completed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/reset-database', methods=['POST'])
def reset_database():
    """Reset the database and clear all team data"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Clear all teams
        success = current_app.db.clear_all_teams()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Database reset successfully. All team data cleared.',
                'teams_count': 0
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reset database'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/reset-database-complete', methods=['POST'])
def reset_database_complete():
    """Completely reset the database by dropping and recreating tables"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return jsonify({
                'success': False,
                'error': message
            }), 503
        
        # Complete database reset
        success = current_app.db.reset_database()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Database completely reset. All tables recreated.',
                'teams_count': 0
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to completely reset database'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """Main page with team selection and prediction"""
    try:
        # Check if database is available
        db_available, message = check_db_available()
        if not db_available:
            return render_template('index.html', 
                                teams_with_stats=[],
                                prediction_result=None,
                                error_message="Database not available. Please try again later.",
                                last_updated=None)
        
        # Get teams with stats
        teams_with_stats = current_app.db.get_all_teams_with_stats()
        
        if not teams_with_stats or len(teams_with_stats) < 10:
            return render_template('index.html',
                                teams_with_stats=[],
                                prediction_result=None,
                                error_message="No VCT data available. Please use the Update button to fetch current tournament data.",
                                last_updated=None)
        
        # Sort teams by record (best to worst)
        def parse_record(record_str):
            """Parse record string like '4-0' to get wins and losses"""
            try:
                if '-' in record_str:
                    wins, losses = map(int, record_str.split('-'))
                    return wins, losses
                elif '–' in record_str:  # Handle en dash
                    wins, losses = map(int, record_str.split('–'))
                    return wins, losses
                else:
                    return 0, 0
            except:
                return 0, 0
        
        def sort_teams(team):
            """Sort key for teams: wins (desc), then losses (asc)"""
            wins, losses = parse_record(team['record'])
            return (-wins, losses)  # Negative wins for descending order
        
        # Sort teams within each group
        teams_with_stats.sort(key=sort_teams)
        
        # Handle form submission for prediction
        prediction_result = None
        error_message = None
        
        if request.method == 'POST':
            try:
                team1_id = request.form.get('team1')
                team2_id = request.form.get('team2')
                
                if not team1_id or not team2_id:
                    error_message = 'Please select two teams'
                elif team1_id == team2_id:
                    error_message = 'Please select two different teams'
                else:
                    # Find the selected teams
                    team1 = next((t for t in teams_with_stats if str(t['id']) == team1_id), None)
                    team2 = next((t for t in teams_with_stats if str(t['id']) == team2_id), None)
                    
                    if not team1 or not team2:
                        error_message = 'One or both selected teams are invalid'
                    elif team1['group_name'] != team2['group_name']:
                        error_message = f'Teams must be from the same group. {team1["team"]} is in Group {team1["group_name"]} and {team2["team"]} is in Group {team2["group_name"]}'
                    else:
                        # Make prediction
                        try:
                            prediction_result = current_app.predictor.predict_match_winner(team1['team'], team2['team'])
                            if 'error' in prediction_result:
                                error_message = prediction_result['error']
                        except Exception as e:
                            error_message = f'Prediction failed: {str(e)}'
                            
            except Exception as e:
                error_message = f'An error occurred: {str(e)}'
        
        # Get last updated time
        last_updated = None
        if teams_with_stats:
            try:
                # Try to get the most recent update time from the database
                last_updated = current_app.db.get_last_update_time()
            except:
                last_updated = datetime.now()
        
        return render_template('index.html',
                            teams_with_stats=teams_with_stats,
                            prediction_result=prediction_result,
                            error_message=error_message,
                            last_updated=last_updated)
                            
    except Exception as e:
        return render_template('index.html',
                            teams_with_stats=[],
                            prediction_result=None,
                            error_message=f"An error occurred: {str(e)}",
                            last_updated=None)
