async function fetchTeamPlayers(teamAbbrev, league = 'nhl') {
  try {
    const url = `http://localhost:3000/api/${league}/teams?team=${teamAbbrev}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error - status: ${response.status}`);
    }
    
    const data = await response.json();
    
    console.log(`Found ${data.count} players for this team`);
    
    return data.players;
    
  } catch (error) {
    console.error('Failed to fetch team data:', error);
    return null;
  }
}

document.addEventListener('DOMContentLoaded', function() {
    const teamButtonsContainer = document.getElementById('team-buttons');
    
    if (teamButtonsContainer) {
        const firstButton = teamButtonsContainer.querySelector('button');
        let league = 'nhl';
        
        if (firstButton) {
            if (firstButton.className.includes('nba')) {
                league = 'nba';
            } else if (firstButton.className.includes('nhl')) {
                league = 'nhl';
            }
        }
        
        teamButtonsContainer.addEventListener('click', function(event) {
            const button = event.target.closest('button');
            if (button) {
                const teamAbbrev = button.dataset.team;
                console.log("clicked", teamAbbrev, league);
                
                window.location.href = `team.html?team=${teamAbbrev}&league=${league}`;
            }
        });
    }
});

// shared script, this is for team.html
async function handleTeamSelection(teamAbbrev, league = 'nhl') {
    const playerDisplay = document.getElementById('player-display');
    
    if (!playerDisplay) return; // don't do it if not on teams
    
    playerDisplay.innerHTML = '<p>Loading team data...</p>';
    
    const players = await fetchTeamPlayers(teamAbbrev, league);
    
    if (players === null) {
        playerDisplay.innerHTML = '<p>Error loading team data. Please try again.</p>';
        return;
    }
    
    displayPlayers(players);
}

function displayPlayers(players) {
    const playerDisplay = document.getElementById('player-display');
    
    let html = '<div class="stats-container">';
    html += '<h2>Team Players</h2>';
    
    if (players.length === 0) {
        html += '<p>No players found for this team.</p>';
    } else {
        html += '<table class="stats-table">';
        html += '<thead><tr>';
        html += '<th class="player-name">Player Name</th>';
        html += '<th class="stat-header">Position</th>';
        html += '<th class="stat-header">Games Played</th>';
        html += '<th class="stat-header">Points</th>';
        html += '<th class="stat-header">Goals</th>';
        html += '<th class="stat-header">Assists</th>';
        html += '</tr></thead>';
        html += '<tbody>';
        
        players.forEach(player => {
            html += '<tr>';
            html += `<td class="player-name">${player.player_name}</td>`;
            html += `<td class="stat-value">${player.position}</td>`;
            html += `<td class="stat-value">${player.games_played}</td>`;
            html += `<td class="stat-value">${player.points}</td>`;
            html += `<td class="stat-value">${player.goals}</td>`;
            html += `<td class="stat-value">${player.assists}</td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table>';
    }
    
    html += '</div>';
    playerDisplay.innerHTML = html;
}

// load data when team param exists
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const teamAbbrev = urlParams.get('team');
    const league = urlParams.get('league') || 'nhl';
    
    if (teamAbbrev && document.getElementById('player-display')) {
        handleTeamSelection(teamAbbrev, league);
    }
});