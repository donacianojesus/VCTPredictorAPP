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

// Form validation
function validateForm() {
    const team1 = document.getElementById('team1').value;
    const team2 = document.getElementById('team2').value;
    const predictButton = document.getElementById('predictButton');
    const team1Help = document.getElementById('team1Help');
    const team2Help = document.getElementById('team2Help');
    
    // Reset help text
    team1Help.style.display = 'none';
    team2Help.style.display = 'none';
    
    let isValid = true;
    
    if (!team1) {
        team1Help.style.display = 'block';
        isValid = false;
    }
    
    if (!team2) {
        team2Help.style.display = 'block';
        isValid = false;
    }
    
    if (team1 && team2) {
        if (teamGroups[team1] !== teamGroups[team2]) {
            team2Help.textContent = 'Teams must be from the same group';
            team2Help.style.display = 'block';
            isValid = false;
        }
    }
    
    predictButton.disabled = !isValid;
    return isValid;
}

// Initialize on page load
function initializePage() {
    // If team1 is pre-selected (from form submission), apply the filter
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    
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
    
    validateForm();
}

// Event listener setup
function setupEventListeners() {
    document.getElementById('team1').addEventListener('change', handleTeam1Change);
    document.getElementById('team2').addEventListener('change', handleTeam2Change);
    document.getElementById('team1').addEventListener('change', validateForm);
    document.getElementById('team2').addEventListener('change', validateForm);
    
    document.getElementById('predictionForm').addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTeamGroups();
    setupEventListeners();
    initializePage();
});
