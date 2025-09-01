const express = require('express');
const fs = require('fs');
const app = express();
const { Pool } = require('pg');
const PORT = process.env.PORT || 3000;
require('dotenv').config({ path: '../../.env' });

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

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});