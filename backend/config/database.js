const Sequelize = require('sequelize');
const dotenv = require('dotenv');

dotenv.config(); // Ensure env vars are loaded

const sequelize = new Sequelize(
    process.env.DB_NAME,
    process.env.DB_USER,
    process.env.DB_PASSWORD,
    {
        host: process.env.DB_HOST || 'localhost',
        dialect: 'mysql',
        logging: false, // Set to true for SQL logging
    }
);

module.exports = sequelize;
