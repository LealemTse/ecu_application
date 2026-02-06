const express = require('express');
const router = express.Router();
const studentController = require('../controllers/studentController');
const verifyToken = require('../middlewares/authMiddleware'); // Protect getters
const multer = require('multer');
const path = require('path');

// Configure Multer Storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/'); // Make sure this folder exists
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage: storage });

// Routes
router.post('/submit', upload.fields([
    { name: 'photo', maxCount: 1 },
    { name: 'transcript', maxCount: 1 },
    { name: 'certificate', maxCount: 1 }
]), studentController.createStudent);

router.get('/', verifyToken, studentController.getAllStudents);
router.get('/:id', verifyToken, studentController.getStudentById);
router.put('/:id', verifyToken, studentController.updateStudent);
router.delete('/:id', verifyToken, studentController.deleteStudent);
router.get('/:id/export', verifyToken, studentController.exportStudentPDF);

module.exports = router;
