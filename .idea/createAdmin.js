require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const MONGO_URI = process.env.MONGO_URI;

const userSchema = new mongoose.Schema({
    username: { type: String, unique: true, required: true },
    passwordHash: { type: String, required: true },
    role: { type: String, default: 'user' }
});
const User = mongoose.model('User', userSchema);

async function createAdmin(username, password) {
    await mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true });
    const existing = await User.findOne({ username });
    if (existing) {
        console.log('User already exists:', username);
        process.exit(0);
    }
    const saltRounds = 10;
    const hash = await bcrypt.hash(password, saltRounds);
    const u = new User({ username, passwordHash: hash, role: 'admin' });
    await u.save();
    console.log('Admin user created:', username);
    process.exit(0);
}

// Usage: node createAdmin.js adminUsername adminPassword
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node createAdmin.js <username> <password>');
    process.exit(1);
}
createAdmin(args[0], args[1]).catch(err => {
    console.error(err);
    process.exit(1);
});
