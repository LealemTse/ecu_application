require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

// Connect to MongoDB
const MONGO_URI = process.env.MONGO_URI;
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.error(err));

// Admin schema
const adminSchema = new mongoose.Schema({
    username: String,
    passwordHash: String,
    role: { type: String, default: 'admin' }
});

const Admin = mongoose.model('Admin', adminSchema);

// Create admin user
async function createAdmin(username, password) {
    const hash = await bcrypt.hash(password, 10);
    const user = new Admin({ username, passwordHash: hash });
    await user.save();
    console.log(`Admin user created: ${username}`);
    mongoose.disconnect();
}

// Replace with your credentials
const username = 'admin';
const password = '12345';

createAdmin(username, password);
