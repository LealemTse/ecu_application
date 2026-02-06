const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const Admin = require('../models/Admin');

const login = async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(400).json({ message: "Username and password are required." });
        }

        const user = await Admin.findOne({ where: { username } });
        if (!user) {
            return res.status(404).json({ message: "Invalid Credentials" });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(401).json({ message: "Invalid Credentials" });
        }

        // Generate Tokens
        const accessToken = jwt.sign(
            { id: user.id, role: 'admin', username: user.username },
            process.env.SESSION_SECRET || 'secret_key_fallback',
            { expiresIn: '15m' }
        );

        const refreshToken = jwt.sign(
            { id: user.id },
            process.env.SESSION_SECRET || 'secret_key_fallback',
            { expiresIn: '7d' }
        );

        // Send Refresh Token in HttpOnly Cookie
        res.cookie("refreshToken", refreshToken, {
            httpOnly: true,
            sameSite: 'lax',
            secure: false, // Set to true in production with HTTPS
            maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
        });

        // Send Access Token in Cookie (for Admin Dashboard simplicity)
        res.cookie("token", accessToken, {
            httpOnly: true,
            sameSite: 'lax',
            secure: false,
            maxAge: 15 * 60 * 1000 // 15 minutes
        });

        res.status(200).json({
            accessToken,
            user: {
                id: user.id,
                username: user.username,
                role: 'admin' // Hardcoded since model doesn't have role yet, or we assume admin
            }
        });

    } catch (err) {
        console.error("Login error:", err);
        res.status(500).json({ message: "Internal Server Error" });
    }
};

const logout = (req, res) => {
    res.clearCookie('refreshToken');
    res.json({ message: "Logged out successfully" });
};

module.exports = { login, logout };
