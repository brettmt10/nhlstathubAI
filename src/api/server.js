const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const cors = require('cors')
const { Pool } = require('pg');
const PORT = process.env.PORT || 3000;
require('dotenv').config({ path: '../../.env' });

// Set EJS as view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../web'));

// app.use(cors({
//   origin: 'http://localhost:8080',
//   methods: ['GET', 'POST', 'PUT', 'DELETE'],
//   credentials: true
// }));

// Serve static files
app.use(express.static(path.join(__dirname, '../web')));

app.get('/', (req, res) => {
  res.render('index');
});

app.get('/nhl', (req, res) => {
  res.render('nhl');
});

app.get('/nba', (req, res) => {
  res.render('nba');
});

app.get('/team', (req, res) => {
  res.render('team');
});


const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: {
    rejectUnauthorized: true,
    ca: fs.readFileSync('rds-ca-rsa2048-g1.pem').toString()
  },
});

app.get('/api/nhl/teams', async (req, res) => {
  try {
    const team = req.query.team;

    // Get players data
    const playersResult = await pool.query(`
      SELECT
      player_name,
      position,
      games_played,
      points,
      goals,
      assists,
      shots,
      blocked_shots,
      toi 
      FROM nhlstage.player_data
      WHERE team_abbrev = $1
      ORDER BY player_name 
    `, [team]);

    // Get team full name
    const teamInfoResult = await pool.query(`
      SELECT team_name
      FROM nhlraw.team_info
      WHERE team_abbrev = $1
    `, [team]);

    res.json({
      success: true,
      count: playersResult.rows.length,
      players: playersResult.rows,
      teamName: teamInfoResult.rows[0]?.team_name || team
    });

    } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/nba/teams', async (req, res) => {
  try {
    const team = req.query.team;

    // Get players data
    const playersResult = await pool.query(`
      SELECT
      player_name,
      position,
      games_played,
      points,
      rebounds, 
      assists,
      steals,
      blocks,
      turnovers,
      minutes 
      FROM nbastage.player_data
      WHERE team_abbrev = $1
      ORDER BY player_name 
    `, [team]);

    // Get team full name
    const teamInfoResult = await pool.query(`
      SELECT team_name
      FROM nbaraw.team_info
      WHERE team_abbrev = $1
    `, [team]);

    res.json({
      success: true,
      count: playersResult.rows.length,
      players: playersResult.rows,
      teamName: teamInfoResult.rows[0]?.team_name || team
    });

    } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});