const express = require('express');
const fs = require('fs');
const app = express();
const cors = require('cors')
const { Pool } = require('pg');
const PORT = process.env.PORT || 3000;
require('dotenv').config({ path: '../../.env' });

app.use(cors({
  origin: 'http://localhost:8080',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));


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

    const result = await pool.query(`
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

    res.json({
      success: true,
      count: result.rows.length,
      players: result.rows
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