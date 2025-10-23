// server.js
require('dotenv').config();
const express = require('express');
const session = require('express-session');
const MongoStore = require('connect-mongo');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const path = require('path');

const app = express();

// Environment variables
const MONGO_URI = process.env.MONGO_URI;
const SESSION_SECRET = process.env.SESSION_SECRET;

// Connect to MongoDB
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.error('MongoDB connection error:', err));

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
        mongoUrl: MONGO_URI,
        collectionName: 'sessions',
    }),
    cookie: {
        httpOnly: true,
        secure: false,
        maxAge: 1000 * 60 * 60 * 2, // 2 hours
    }
}));

// Serve static files (login.html, admin.html, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// Admin schema
const adminSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    passwordHash: { type: String, required: true },
    role: { type: String, default: 'admin' }
});

const Admin = mongoose.model('Admin', adminSchema);

// Middleware to protect admin page
function requireLogin(req, res, next) {
    if (!req.session.userId) {
        return res.redirect('/');
    }
    next();
}

// Routes

// Root → login page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Admin page (protected)
app.get('/admin.html', requireLogin, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// Login handler
app.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) return res.redirect('/');

        const user = await Admin.findOne({ username });
        if (!user) return res.redirect('/');

        const ok = await bcrypt.compare(password, user.passwordHash);
        if (!ok) return res.redirect('/');

        // Success
        req.session.userId = user._id;
        req.session.username = user.username;
        req.session.role = user.role;

        res.redirect('/admin.html');
    } catch (err) {
        console.error('Login error', err);
        res.redirect('/');
    }
});

// Logout route
app.get('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) console.error(err);
        res.redirect('/');
    });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
