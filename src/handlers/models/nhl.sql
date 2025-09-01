# WORKING NHL

CREATE TABLE IF NOT EXISTS nhlraw.player_data (
    player_id INTEGER,
	player_name VARCHAR(255) NOT NULL,
    team_abbrev VARCHAR(10) NOT NULL,
    position VARCHAR(5),
    games_played INTEGER,
    points INTEGER,
    goals INTEGER,
    assists INTEGER,
    shots INTEGER,
    blocked_shots INTEGER,
    toi DECIMAL(5,2),
    salary INTEGER,
    ppg DECIMAL(5,3)
);

CREATE TABLE IF NOT EXISTS nhlraw.player_info (
    player_id INTEGER,
	player_name VARCHAR(255) NOT NULL,
    team_abbrev VARCHAR(10) NOT NULL,
    position VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS nhlraw.player_game_log (
    player_id INTEGER,
    player_name VARCHAR(100),
    home_road_flag CHAR(1),
    game_date DATE,
    goals INTEGER,
    assists INTEGER,
    opponent_common_name VARCHAR(50),
    points INTEGER,
    shots INTEGER,
    toi FLOAT
);

CREATE VIEW nhlstage.player_data AS (
	SELECT
	    b.player_id,
	    b.player_name, 
	    b.team_abbrev, 
	    b.position,
		SUM(a.games_played) AS games_played,
		SUM(a.points) as points,
		SUM(a.goals) as goals,
		SUM(a.assists) as assists,
		SUM(a.shots) as shots,
		SUM(a.blocked_shots) as blocked_shots,
		SUM(CASE WHEN a.team_abbrev = b.team_abbrev THEN a.toi ELSE 0 END) AS toi
	FROM nhlraw.player_data a
	RIGHT JOIN nhlraw.player_info b on a.player_id = b.player_id and a.position != 'G'
	WHERE a.games_played IS NOT NULL
	GROUP BY b.player_id, b.player_name, b.team_abbrev, b.position
);

CREATE OR REPLACE VIEW nhlstage.player_game_log AS (
	SELECT
        a.player_id,
		a.player_name,
		b.team_abbrev as current_team,
		a.game_date as date,
		a.opponent_common_name as matchup,
		a.home_road_flag as homevroad,
		a.points,
		a.goals,
		a.assists,
		a.shots,
		a.toi
	FROM nhlraw.player_game_log a
	LEFT JOIN nhlraw.player_info b
	ON a.player_id = b.player_id
);