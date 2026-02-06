const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
    const token =
        (req.cookies && req.cookies.token) ||
        (req.body && req.body.token) ||
        req.query.token ||
        req.headers["x-access-token"] ||
        req.headers["authorization"];

    if (!token) {
        return res.status(403).json({ message: "A token is required for authentication" });
    }

    try {
        // Handle "Bearer <token>" format
        const bearerToken = token.startsWith('Bearer ') ? token.slice(7, token.length) : token;

        const decoded = jwt.verify(bearerToken, process.env.SESSION_SECRET || 'secret_key_fallback');
        req.user = decoded;
    } catch (err) {
        return res.status(401).json({ message: "Invalid Token" });
    }
    return next();
};

module.exports = verifyToken;
