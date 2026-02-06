const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Student = sequelize.define('Student', {
    // Personal Profile
    firstName: { type: DataTypes.STRING, allowNull: false },
    middleName: { type: DataTypes.STRING, allowNull: false },
    lastName: { type: DataTypes.STRING, allowNull: false },
    phoneNumber: { type: DataTypes.STRING, allowNull: false },
    email: { type: DataTypes.STRING, allowNull: false, unique: true },
    dateOfBirth: { type: DataTypes.DATEONLY, allowNull: false },
    placeOfBirth: { type: DataTypes.STRING, allowNull: false },
    nationality: { type: DataTypes.STRING, allowNull: false },

    // Address
    country: { type: DataTypes.STRING, allowNull: false },
    region: { type: DataTypes.STRING, allowNull: false },
    city: { type: DataTypes.STRING, allowNull: false },
    subCity: { type: DataTypes.STRING, allowNull: false },
    woreda: { type: DataTypes.STRING, allowNull: false },

    // Details
    gender: { type: DataTypes.ENUM('male', 'female'), allowNull: false },
    maritalStatus: { type: DataTypes.ENUM('single', 'married', 'divorced', 'widowed'), allowNull: false },
    disabilities: { type: DataTypes.ENUM('yes', 'no'), allowNull: false },

    // Contact Person
    guardianName: { type: DataTypes.STRING, allowNull: false },
    guardianMobile: { type: DataTypes.STRING, allowNull: false },
    guardianPhone: { type: DataTypes.STRING, allowNull: false },
    guardianCountry: { type: DataTypes.STRING, allowNull: false },
    guardianRegion: { type: DataTypes.STRING, allowNull: false },
    guardianCity: { type: DataTypes.STRING, allowNull: false },
    guardianSubCity: { type: DataTypes.STRING, allowNull: false },
    guardianWoreda: { type: DataTypes.STRING, allowNull: false },

    // Academic Profile
    highSchoolName: { type: DataTypes.STRING, allowNull: false },
    highSchoolAddress: { type: DataTypes.STRING, allowNull: false },
    highSchoolStart: { type: DataTypes.STRING, allowNull: false },
    highSchoolEnd: { type: DataTypes.STRING, allowNull: false },
    multipleSchools: { type: DataTypes.ENUM('yes', 'no'), allowNull: false },

    // Additional Schools (Dynamic)
    additionalSchools: {
        type: DataTypes.JSON,
        defaultValue: []
        // Stores array of objects: { name, address, start, end }
    },

    // Science Stream
    scienceStream: { type: DataTypes.ENUM('natural', 'social'), allowNull: false },

    // Exam Results (Stored as JSON for flexibility or separate columns)
    // Using separate columns for clarity and queryability
    resultSubject1: { type: DataTypes.STRING }, // e.g. Physics/Geography
    resultScore1: { type: DataTypes.INTEGER },
    resultSubject2: { type: DataTypes.STRING }, // e.g. Math
    resultScore2: { type: DataTypes.INTEGER },
    resultSubject3: { type: DataTypes.STRING }, // e.g. English
    resultScore3: { type: DataTypes.INTEGER },
    resultSubject4: { type: DataTypes.STRING }, // e.g. Chem/Econ
    resultScore4: { type: DataTypes.INTEGER },
    resultSubject5: { type: DataTypes.STRING }, // e.g. Bio/History
    resultScore5: { type: DataTypes.INTEGER },
    resultSubject6: { type: DataTypes.STRING }, // e.g. Aptitude
    resultScore6: { type: DataTypes.INTEGER },
    resultSubject7: { type: DataTypes.STRING }, // e.g. Civics
    resultScore7: { type: DataTypes.INTEGER },
    totalScore: { type: DataTypes.INTEGER, allowNull: false },
    examYear: { type: DataTypes.STRING },

    // Field of Study
    fieldOfStudy: { type: DataTypes.STRING, allowNull: false },

    // Files (Paths)
    photoPath: { type: DataTypes.STRING },
    transcriptPath: { type: DataTypes.STRING },
    certificatePath: { type: DataTypes.STRING },

    // Status
    status: { type: DataTypes.ENUM('pending', 'approved', 'rejected'), defaultValue: 'pending' }

});

module.exports = Student;
