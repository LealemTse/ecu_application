// server.js
require('dotenv').config();
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const sequelize = require('./config/database');

// Routes
const authRoutes = require('./routes/authRoutes');
const studentRoutes = require('./routes/studentRoutes');

const app = express();

// Environment variables
const PORT = process.env.PORT || 3000;

// Connect to MySQL
sequelize.authenticate()
    .then(() => console.log('MySQL connected'))
    .catch(err => console.error('MySQL connection error:', err));

// Sync Database
// Force: false ensures we don't drop tables, alter: true updates schema if possible
sequelize.sync({ alter: true })
    .then(() => console.log('Database synced'))
    .catch(err => console.error('Database sync error:', err));

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(cors());

// Serve static files
app.use(express.static(path.join(__dirname, '../frontend')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads'))); // Serve uploaded files

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/students', studentRoutes);

// Root → login page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend', 'login.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
