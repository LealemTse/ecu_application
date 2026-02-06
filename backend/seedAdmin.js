const sequelize = require('./config/database');
const Admin = require('./models/Admin');

const seedAdmin = async () => {
    try {
        await sequelize.authenticate();
        console.log('Database connected.');
        // Force sync to update table structure if it changed (remove columns)
        // correct way to drop/create is force:true, or alter:true
        await sequelize.sync({ alter: true });

        const username = process.env.ADMIN_USER || 'admin';
        const password = process.env.ADMIN_PASSWORD;

        if (!password) {
            console.error('ADMIN_PASSWORD not set. Aborting seed.');
            process.exit(1);
        }

        // Check if admin exists
        const existingAdmin = await Admin.findOne({ where: { username } });
        if (existingAdmin) {
            console.log('Admin user already exists.');
            process.exit(0);
        }

        await Admin.create({
            username,
            password
        });

        console.log('Admin user seeded successfully.');
        process.exit(0);
    } catch (error) {
        console.error('Error seeding admin:', error);
        process.exit(1);
    }
};

seedAdmin();
