require('dotenv').config();
const path = require('path');
const express = require('express');
const mongoose = require('mongoose');
const session = require('express-session');
const MongoStore = require('connect-mongo')(session);
const bcrypt = require('bcrypt');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI;
const SESSION_SERVER_URI = process.env.SESSION_SERVER || 'romxok-gawtyB-5cuvta';


// ------Mongoose User Modeling----------
mongoose.connect(MONGODB_URI, {useNewUrlParser: true, useUnifiedTopology: true})
    .then(() => console.log('Connected to the MongoDB'))
    .catch(err => {
        console.error("MongoDB connection error:", err);
        process.exit(1);
    });

//for-user
const userSchema = new mongoose.Schema({
    username: {type: String, unique: true, required: true},
    password: {type: String, required: true},
    role: {type: String, default: 'Administrator'},
})

const User = mongoose.model('Admin', userSchema);

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use(session({
    secret: SESSION_SERVER,
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
        mongoUrl: MONGODB_URI,
        collection: 'sessions',
    }),
    cookie:{
        httpOnly: true,
        secure: false,
        maxAge: 1000 * 60 * 24 * 7,
    }
}));

app.use(express.static(path.join(__dirname, 'public')));


function requireAuth(req, res, next) {
    if(req.session && req.session.userID) {
        return next();
    }
    if (req.xhr || req.headers.accept.indexOf('application/json') > -1) {
        return res.status(401).json({error: 'Unauthorized'});
    }
    return res.redirect('./login.html');
}

//---Routes-----
app.post('/login', async (req, res) => {
    try{
        const {username, password} = req.body;
        if(!username || !password){
            return res.status(400).send('Username or Password is required');
        }

        const user = await User.findOne({username});
        if(!user){
            return res.status(401).send('Invalid credentials');
        }

        const ok = await bcrypt.compare(password, user.passwordHash);
        if(!ok){
            return res.status(401).send('Invalid credentials');
        }

        req.session.userID = user.id;
        req.session.username = user.username;
        req.session.role = user.role;
        return res.redirect('/admin');
    }catch (err){
        console.error('Login error: ', err);
        return res.status(500).send('Server Error');
    }
});

//GET /admin - proteced
app.get('/admin', requireAuth, (req, res) => {
    return res.sendFile(path.join(__dirname, 'public', './admin.html'));
});

app.get('/api/me', requireAuth, (req, res) => {
    res.json({username: req.session, role: req.session.role});
});
app.post('/logout', (req, res) => {
    req.session.destroy(err=> {
        if (err){
            console.error('Session destroyed error');
            return res.status(500).send('logout failed');
        }
        res.clearCookie('connect.sid');
        return res.redirect('/login.html');
    });
});

app.get('/ping', (req, res) => res.send('pong'));
app.listen(PORT, ()=> console.log(`Server runnig on http://localhost:${PORT}`));

