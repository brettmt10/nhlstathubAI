async function fetchTeamPlayers(teamAbbrev) {
  try {
    const url = `http://localhost:3000/api/nhl/teams?team=${teamAbbrev}`;
    
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
    
    teamButtonsContainer.addEventListener('click', function(event) {
        const button = event.target.closest('button');
        if (button) {
            const teamAbbrev = button.dataset.team;
            console.log("clicked")
            
            window.location.href = `team.html?team=${teamAbbrev}`;
        }
    });
});

// shared script, this is for team.html
async function handleTeamSelection(teamAbbrev) {
    const playerDisplay = document.getElementById('player-display');
    
    if (!playerDisplay) return; // don't do it if not on teams
    
    playerDisplay.innerHTML = '<p>Loading team data...</p>';
    
    const players = await fetchTeamPlayers(teamAbbrev);
    
    if (players === null) {
        playerDisplay.innerHTML = '<p>Error loading team data. Please try again.</p>';
        return;
    }
    
    displayPlayers(players);
}

function displayPlayers(players) {
    const playerDisplay = document.getElementById('player-display');
    
    let html = '<h2>Team Players</h2>';
    
    if (players.length === 0) {
        html += '<p>No players found for this team.</p>';
    } else {
        html += '<table border="1">';
        html += '<tr><th>Player Name</th><th>Position</th><th>Games Played</th><th>Points</th><th>Goals</th><th>Assists</th></tr>';
        
        players.forEach(player => {
            html += '<tr>';
            html += `<td>${player.player_name}</td>`;
            html += `<td>${player.position}</td>`;
            html += `<td>${player.games_played}</td>`;
            html += `<td>${player.points}</td>`;
            html += `<td>${player.goals}</td>`;
            html += `<td>${player.assists}</td>`;
            html += '</tr>';
        });
        
        html += '</table>';
    }
    
    playerDisplay.innerHTML = html;
}

// load data when team param exists
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const teamAbbrev = urlParams.get('team');
    
    if (teamAbbrev && document.getElementById('player-display')) {
        handleTeamSelection(teamAbbrev);
    }
});