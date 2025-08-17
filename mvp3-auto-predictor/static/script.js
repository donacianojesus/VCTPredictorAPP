// VCT Predictor - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 VCT Predictor JavaScript loaded');
    
    // Get DOM elements
    const updateBtn = document.getElementById('updateDataBtn');
    const resetBtn = document.getElementById('resetDataBtn');
    const completeResetBtn = document.getElementById('completeResetBtn');
    const updateStatus = document.getElementById('updateStatus');
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    const predictBtn = document.querySelector('.predict-btn');
    
    // Debug: Log all found elements
    console.log('🔍 Found elements:', {
        updateBtn: !!updateBtn,
        resetBtn: !!resetBtn,
        completeResetBtn: !!completeResetBtn,
        updateStatus: !!updateStatus,
        team1Select: !!team1Select,
        team2Select: !!team2Select,
        predictBtn: !!predictBtn
    });
    
    // Update Data Button Functionality
    if (updateBtn) {
        updateBtn.addEventListener('click', function() {
            updateVCTData();
        });
    }
    
    // Reset Database Button Functionality
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetDatabase();
        });
    }
    
    // Complete Reset Database Button Functionality
    if (completeResetBtn) {
        completeResetBtn.addEventListener('click', function() {
            completeResetDatabase();
        });
    }
    
    // Team Selection Validation
    if (team1Select && team2Select && predictBtn) {
        console.log('✅ Team selection elements found, setting up validation');
        console.log('🎯 Predict button found:', predictBtn);
        console.log('🎯 Team1 select found:', team1Select);
        console.log('🎯 Team2 select found:', team2Select);
        
        // Function to validate team selection
        function validateTeamSelection() {
            const team1Value = team1Select.value;
            const team2Value = team2Select.value;
            
            console.log('🔍 Validating teams:', team1Value, team2Value);
            console.log('🔍 Button current state:', predictBtn.disabled);
            
            if (team1Value && team2Value) {
                if (team1Value === team2Value) {
                    console.log('❌ Same team selected - disabling button');
                    predictBtn.disabled = true;
                    predictBtn.title = 'Please select two different teams';
                } else {
                    console.log('✅ Different teams selected - enabling button');
                    predictBtn.disabled = false;
                    predictBtn.title = 'Click to predict the winner';
                }
            } else {
                console.log('❌ Missing team selection - disabling button');
                predictBtn.disabled = true;
                predictBtn.title = 'Please select two teams';
            }
            
            console.log('🔍 Button final state:', predictBtn.disabled);
        }
        
        // Add event listeners
        team1Select.addEventListener('change', function() {
            console.log('🔄 Team1 changed to:', this.value);
            validateTeamSelection();
        });
        team2Select.addEventListener('change', function() {
            console.log('🔄 Team2 changed to:', this.value);
            validateTeamSelection();
        });
        
        // Initial validation
        console.log('🚀 Running initial validation...');
        validateTeamSelection();
        
        // Debug: Log all options
        console.log('📋 All team options:');
        for (let i = 0; i < team1Select.options.length; i++) {
            const option = team1Select.options[i];
            console.log(`  Option ${i}: "${option.text}" - Value: "${option.value}"`);
        }
        
        // Test: Manually trigger validation after a delay
        setTimeout(() => {
            console.log('⏰ Delayed validation test...');
            validateTeamSelection();
        }, 1000);
        
    } else {
        console.log('⚠️ Team selection elements not found');
        if (!team1Select) console.log('❌ team1Select not found');
        if (!team2Select) console.log('❌ team2Select not found');
        if (!predictBtn) console.log('❌ predictBtn not found');
        
        // Try alternative selectors
        const altPredictBtn = document.querySelector('button[type="submit"]');
        console.log('🔍 Alternative button selector:', altPredictBtn);
        
        const altPredictBtn2 = document.querySelector('.prediction-form button');
        console.log('🔍 Alternative button selector 2:', altPredictBtn2);
    }
    
    // Debug: Check loading spinner states on page load
    console.log('🔍 Checking loading spinner states on page load...');
    const allLoadingSpinners = document.querySelectorAll('.loading-spinner');
    console.log(`Found ${allLoadingSpinners.length} loading spinners`);
    
    allLoadingSpinners.forEach((spinner, index) => {
        const isVisible = spinner.style.display !== 'none';
        console.log(`Spinner ${index}: visible=${isVisible}, display=${spinner.style.display}`);
        
        // Ensure all spinners are hidden on page load
        if (isVisible) {
            console.log(`🔄 Hiding spinner ${index} on page load`);
            spinner.style.display = 'none';
        }
    });
    
    // Debug: Check button states on page load
    console.log('🔍 Checking button states on page load...');
    if (updateBtn) {
        const updateBtnText = updateBtn.querySelector('.btn-text');
        const updateBtnSpinner = updateBtn.querySelector('.loading-spinner');
        console.log('Update button:', {
            disabled: updateBtn.disabled,
            textVisible: updateBtnText.style.display !== 'none',
            spinnerVisible: updateBtnSpinner.style.display !== 'none'
        });
    }
    
    // Update VCT Data Function
    function updateVCTData() {
        if (!updateBtn) return;
        
        // Disable button and show loading
        updateBtn.disabled = true;
        updateBtn.querySelector('.btn-text').style.display = 'none';
        updateBtn.querySelector('.loading-spinner').style.display = 'inline-block';
        updateStatus.textContent = 'Updating VCT data...';
        updateStatus.className = 'update-status info';
        
        // Make API call to update data
        fetch('/api/run-scraper', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus.textContent = `✅ Data updated successfully! Found ${data.teams_count} teams`;
                updateStatus.className = 'update-status success';
                
                // Refresh the page to show new data
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                updateStatus.textContent = `❌ Update failed: ${data.error || 'Unknown error'}`;
                updateStatus.className = 'update-status error';
            }
        })
        .catch(error => {
            updateStatus.textContent = `❌ Update failed: ${error.message}`;
            updateStatus.className = 'update-status error';
        })
        .finally(() => {
            // Re-enable button and hide loading
            updateBtn.disabled = false;
            updateBtn.querySelector('.btn-text').style.display = 'inline';
            updateBtn.querySelector('.loading-spinner').style.display = 'none';
        });
    }
    
    // Reset Database Function
    function resetDatabase() {
        if (!resetBtn) return;
        
        // Confirm before resetting
        if (!confirm('⚠️ Are you sure you want to reset the database? This will delete ALL team data and cannot be undone.')) {
            return;
        }
        
        // Disable button and show loading
        resetBtn.disabled = true;
        resetBtn.querySelector('.btn-text').style.display = 'none';
        resetBtn.querySelector('.loading-spinner').style.display = 'inline-block';
        updateStatus.textContent = 'Resetting database...';
        updateStatus.className = 'update-status info';
        
        // Make API call to reset database
        fetch('/api/reset-database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus.textContent = '✅ Database reset successfully! All team data cleared.';
                updateStatus.className = 'update-status success';
                
                // Refresh the page to show empty state
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                updateStatus.textContent = `❌ Reset failed: ${data.error || 'Unknown error'}`;
                updateStatus.className = 'update-status error';
            }
        })
        .catch(error => {
            updateStatus.textContent = `❌ Reset failed: ${error.message}`;
            updateStatus.className = 'update-status error';
        })
        .finally(() => {
            // Re-enable button and hide loading
            resetBtn.disabled = false;
            resetBtn.querySelector('.btn-text').style.display = 'inline';
            resetBtn.querySelector('.loading-spinner').style.display = 'none';
        });
    }
    
    // Complete Reset Database Function
    function completeResetDatabase() {
        if (!completeResetBtn) return;
        
        // Confirm before complete reset
        if (!confirm('⚠️ Are you sure you want to COMPLETELY reset the database? This will DROP and RECREATE all tables. This action cannot be undone and will lose ALL data.')) {
            return;
        }
        
        // Disable button and show loading
        completeResetBtn.disabled = true;
        completeResetBtn.querySelector('.btn-text').style.display = 'none';
        completeResetBtn.querySelector('.loading-spinner').style.display = 'inline-block';
        updateStatus.textContent = 'Completely resetting database...';
        updateStatus.className = 'update-status info';
        
        // Make API call to completely reset database
        fetch('/api/reset-database-complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus.textContent = '✅ Database completely reset! All tables recreated.';
                updateStatus.className = 'update-status success';
                
                // Refresh the page to show empty state
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                updateStatus.textContent = `❌ Complete reset failed: ${data.error || 'Unknown error'}`;
                updateStatus.className = 'update-status error';
            }
        })
        .catch(error => {
            updateStatus.textContent = `❌ Complete reset failed: ${error.message}`;
            updateStatus.className = 'update-status error';
        })
        .finally(() => {
            // Re-enable button and hide loading
            completeResetBtn.disabled = false;
            completeResetBtn.querySelector('.btn-text').style.display = 'inline';
            completeResetBtn.querySelector('.loading-spinner').style.display = 'none';
        });
    }
    
    console.log('🎉 VCT Predictor initialization complete');
});
