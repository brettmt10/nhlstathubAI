# CURRENT WORKING NBA
CREATE TABLE IF NOT EXISTS nbaraw.player_info (
    player_id INTEGER,
	player_name VARCHAR(255) NOT NULL,
    team_abbrev VARCHAR(10) NOT NULL,
    position VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS nbaraw.player_data (
    player_id INTEGER,
    player_name VARCHAR(255),
    team_abbrev VARCHAR(10),
	games_played INTEGER,
	points FLOAT,
	rebounds FLOAT,
	assists FLOAT,
	turnovers FLOAT,
    steals FLOAT,
    blocks FLOAT,
	minutes FLOAT
);

CREATE TABLE IF NOT EXISTS nbaraw.player_game_log (
    player_id INTEGER,
    player_name VARCHAR(255),
    homevaway VARCHAR(50),
    date DATE,
    points FLOAT,
    rebounds FLOAT,
    assists FLOAT,
    turnovers FLOAT,
    steals FLOAT,
    blocks FLOAT,
    minutes FLOAT
);

CREATE VIEW nbastage.player_data AS
SELECT 
    b.player_name, 
    b.team_abbrev, 
    b.position,
    SUM(a.games_played) AS games_played,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.points ELSE 0 END) AS points,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.rebounds ELSE 0 END) AS rebounds,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.assists ELSE 0 END) AS assists,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.turnovers ELSE 0 END) AS turnovers,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.steals ELSE 0 END) AS steals,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.blocks ELSE 0 END) AS blocks,
    SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.minutes ELSE 0 END) AS minutes
FROM nbaraw.player_data a
RIGHT JOIN nbaraw.player_info b ON a.player_id = b.player_id
GROUP BY b.player_id, b.player_name, b.team_abbrev, b.position;

CREATE OR REPLACE VIEW nbastage.player_game_log AS (
	SELECT
		a.player_name,
		b.team_abbrev as current_team,
		a.homevaway as matchup,
		a.date as date,
		a.points,
		a.rebounds,
		a.assists,
		a.turnovers,
		a.steals,
		a.blocks,
		a.minutes
	FROM nbaraw.player_game_log a
	LEFT JOIN nbaraw.player_info b
	ON a.player_id = b.player_id
);