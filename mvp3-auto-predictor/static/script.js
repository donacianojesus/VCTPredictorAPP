// Enhanced VCT Match Predictor JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize health monitoring
    loadScraperHealth();
    
    // Set up form validation and submission
    setupFormValidation();
    
    // Initialize team group filtering
    initializeTeamGroups();
    
    // Auto-refresh health status every 30 seconds
    setInterval(loadScraperHealth, 30000);
});

// Get team group information from the page
const teamGroups = {};

// Extract team group information from the optgroups
function initializeTeamGroups() {
    document.querySelectorAll('optgroup').forEach(group => {
        const groupName = group.label.replace('Group ', '');
        group.querySelectorAll('option').forEach(option => {
            if (option.value) {
                teamGroups[option.value] = groupName;
            }
        });
    });
}

// Function to filter teams by group
function filterTeamsByGroup(teamSelect, targetGroup) {
    const optgroups = teamSelect.querySelectorAll('optgroup');
    
    optgroups.forEach(group => {
        const groupName = group.label.replace('Group ', '');
        const options = group.querySelectorAll('option');
        
        options.forEach(option => {
            if (option.value) {
                if (groupName === targetGroup) {
                    option.style.display = '';
                    option.disabled = false;
                } else {
                    option.style.display = 'none';
                    option.disabled = true;
                }
            }
        });
    });
}

// Function to show all teams
function showAllTeams(teamSelect) {
    const optgroups = teamSelect.querySelectorAll('optgroup');
    
    optgroups.forEach(group => {
        const options = group.querySelectorAll('option');
        options.forEach(option => {
            if (option.value) {
                option.style.display = '';
                option.disabled = false;
            }
        });
    });
}

// Handle team1 selection
function handleTeam1Change() {
    const team2Select = document.getElementById('team2');
    const selectedValue = this.value;
    
    // Reset team2 selection
    team2Select.value = '';
    
    if (selectedValue) {
        const selectedTeamGroup = teamGroups[selectedValue];
        
        // Filter team2 dropdown to only show teams from the same group
        filterTeamsByGroup(team2Select, selectedTeamGroup);
        
        // Disable the selected team in team2 dropdown
        const options = team2Select.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === selectedValue) {
                option.disabled = true;
            }
        });
        
        // Update the placeholder text
        team2Select.querySelector('option[value=""]').textContent = `-- Select Team 2 (Group ${selectedTeamGroup}) --`;
    } else {
        // If no team selected, show all teams
        showAllTeams(team2Select);
        team2Select.querySelector('option[value=""]').textContent = '-- Select Team 2 --';
    }
}

// Handle team2 selection
function handleTeam2Change() {
    const team1Select = document.getElementById('team1');
    const selectedValue = this.value;
    
    if (selectedValue) {
        // Disable the selected team in team1 dropdown
        const options = team1Select.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === selectedValue) {
                option.disabled = true;
            }
        });
    }
}

function loadScraperHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            updateHealthDisplay(data);
        })
        .catch(error => {
            console.error('Failed to load health data:', error);
            updateHealthDisplay({
                status: 'error',
                message: 'Failed to load health data',
                last_run: 'Unknown',
                success_count: 0,
                total_runs: 0
            });
        });
}

function updateHealthDisplay(healthData) {
    // Update health values
    document.getElementById('lastRun').textContent = formatLastRun(healthData.last_run);
    document.getElementById('scraperStatus').textContent = healthData.status;
    document.getElementById('successRate').textContent = calculateSuccessRate(healthData.success_count, healthData.total_runs);
    document.getElementById('totalRuns').textContent = healthData.total_runs;
    
    // Update health message
    const healthMessage = document.getElementById('healthMessage');
    healthMessage.textContent = healthData.message || '';
    
    // Update status colors
    updateStatusColors(healthData.status);
}

function formatLastRun(lastRun) {
    if (!lastRun || lastRun === 'Unknown') return 'Unknown';
    
    try {
        const date = new Date(lastRun);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays > 0) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else {
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
        }
    } catch (e) {
        return 'Unknown';
    }
}

function calculateSuccessRate(successCount, totalRuns) {
    if (totalRuns === 0) return '0%';
    return `${Math.round((successCount / totalRuns) * 100)}%`;
}

function updateStatusColors(status) {
    const statusElement = document.getElementById('scraperStatus');
    statusElement.className = 'health-value status-' + status;
}

function setupFormValidation() {
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    const predictButton = document.getElementById('predictButton');
    
    // Add event listeners for team selection
    team1Select.addEventListener('change', handleTeam1Change);
    team2Select.addEventListener('change', handleTeam2Change);
    
    // Function to check if form is valid
    function validateForm() {
        const team1 = team1Select.value;
        const team2 = team2Select.value;
        
        if (team1 && team2 && team1 !== team2) {
            predictButton.disabled = false;
            predictButton.classList.add('ready');
        } else {
            predictButton.disabled = true;
            predictButton.classList.remove('ready');
        }
    }
    
    // Add event listeners
    team1Select.addEventListener('change', validateForm);
    team2Select.addEventListener('change', validateForm);
    
    // Initial validation
    validateForm();
    
    // Enhanced form submission with loading state
    document.getElementById('predictionForm').addEventListener('submit', function(e) {
        if (predictButton.disabled) {
            e.preventDefault();
            return;
        }
        
        // Show loading state
        predictButton.disabled = true;
        predictButton.innerHTML = '<span class="loading-spinner"></span> Predicting...';
        
        // Re-enable after a delay (form will submit)
        setTimeout(() => {
            predictButton.disabled = false;
            predictButton.innerHTML = 'Predict Match Winner';
        }, 2000);
    });
    
    // Initialize page state if teams are pre-selected
    if (team1Select.value) {
        const selectedTeamGroup = teamGroups[team1Select.value];
        filterTeamsByGroup(team2Select, selectedTeamGroup);
        
        // Disable the selected team in team2 dropdown
        const options = team2Select.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === team1Select.value) {
                option.disabled = true;
            }
        });
        
        // Update the placeholder text
        team2Select.querySelector('option[value=""]').textContent = `-- Select Team 2 (Group ${selectedTeamGroup}) --`;
    }
    
    // Also handle team2 pre-selection
    if (team2Select.value) {
        const options = team1Select.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === team2Select.value) {
                option.disabled = true;
            }
        });
    }
}

// Add smooth scrolling for better UX
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Add keyboard navigation for form
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName === 'SELECT') {
        e.preventDefault();
        const nextElement = e.target.nextElementSibling;
        if (nextElement && nextElement.tagName === 'SELECT') {
            nextElement.focus();
        }
    }
});

// Add loading animation CSS
const style = document.createElement('style');
style.textContent = `
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .status-success {
        color: #4caf50;
    }
    
    .status-error {
        color: #f44336;
    }
    
    .status-warning {
        color: #ff9800;
    }
    
    .ready {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .health-item {
        transition: all 0.3s ease;
    }
    
    .health-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
`;
document.head.appendChild(style);
