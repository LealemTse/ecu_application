const Student = require('../models/Student');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Create new student application
exports.createStudent = async (req, res) => {
    try {
        const studentData = { ...req.body };

        // Handle files
        if (req.files) {
            if (req.files.photo) studentData.photoPath = req.files.photo[0].path;
            if (req.files.transcript) studentData.transcriptPath = req.files.transcript[0].path;
            if (req.files.certificate) studentData.certificatePath = req.files.certificate[0].path;
        }

        // Handle Additional Schools (Parse from req.body)
        const additionalSchools = [];
        const schoolKeys = Object.keys(studentData).filter(k => k.startsWith('additionalSchool'));

        // Group by index
        const schoolsMap = {};
        schoolKeys.forEach(key => {
            // key format: additionalSchool[0][name]
            const match = key.match(/additionalSchool\[(\d+)\]\[(\w+)\]/);
            if (match) {
                const index = match[1];
                const field = match[2]; // name, address, start, end
                if (!schoolsMap[index]) schoolsMap[index] = {};
                schoolsMap[index][field] = studentData[key];

                // Remove the raw key from studentData so it doesn't clutter
                delete studentData[key];
            }
        });

        // Convert map to array
        Object.keys(schoolsMap).sort().forEach(index => {
            additionalSchools.push(schoolsMap[index]);
        });

        studentData.additionalSchools = additionalSchools;

        // Validate dateOfBirth - if invalid, set to null
        if (studentData.dateOfBirth === 'Invalid date' || studentData.dateOfBirth === '' || !studentData.dateOfBirth) {
            studentData.dateOfBirth = null;
        }

        const newStudent = await Student.create(studentData);
        res.status(201).json({ message: 'Application submitted successfully', studentId: newStudent.id });
    } catch (error) {
        console.error('Error submitting application:', error);
        res.status(500).json({ message: 'Error submitting application', error: error.message });
    }
};

// Get all students
exports.getAllStudents = async (req, res) => {
    try {
        const students = await Student.findAll();
        res.status(200).json(students);
    } catch (error) {
        console.error('Error fetching students:', error);
        res.status(500).json({ message: 'Error fetching students' });
    }
};

// Get single student by ID
exports.getStudentById = async (req, res) => {
    try {
        const student = await Student.findByPk(req.params.id);
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }
        res.status(200).json(student);
    } catch (error) {
        console.error('Error fetching student:', error);
        res.status(500).json({ message: 'Error fetching student' });
    }
};

// Update student
exports.updateStudent = async (req, res) => {
    try {
        const { id } = req.params;
        let updateData = { ...req.body };

        const student = await Student.findByPk(id);
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        // Handle Additional Schools if present
        const additionalSchools = [];
        const schoolKeys = Object.keys(updateData).filter(k => k.startsWith('additionalSchool'));

        if (schoolKeys.length > 0) {
            const schoolsMap = {};
            schoolKeys.forEach(key => {
                const match = key.match(/additionalSchool\[(\d+)\]\[(\w+)\]/);
                if (match) {
                    const index = match[1];
                    const field = match[2];
                    if (!schoolsMap[index]) schoolsMap[index] = {};
                    schoolsMap[index][field] = updateData[key];
                    delete updateData[key];
                }
            });
            Object.keys(schoolsMap).sort().forEach(index => {
                additionalSchools.push(schoolsMap[index]);
            });
            updateData.additionalSchools = additionalSchools;
        }

        await student.update(updateData);
        res.status(200).json({ message: 'Student updated successfully', student });
    } catch (error) {
        console.error('Error updating student:', error);
        res.status(500).json({ message: 'Error updating student' });
    }
};

// Export to PDF
exports.exportStudentPDF = async (req, res) => {
    try {
        const student = await Student.findByPk(req.params.id);
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        // Create temp JSON data file
        const tempDir = path.join(__dirname, '../temp');
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });

        const tempJsonPath = path.join(tempDir, `student_${student.id}.json`);

        // Prepare data with absolute paths for the python script
        const studentData = student.toJSON();

        // Helper to resolve absolute path
        const resolvePath = (p) => p ? path.resolve(__dirname, '..', p) : null;

        if (studentData.photoPath) studentData.photoPath = resolvePath(studentData.photoPath);
        if (studentData.transcriptPath) studentData.transcriptPath = resolvePath(studentData.transcriptPath);
        if (studentData.certificatePath) studentData.certificatePath = resolvePath(studentData.certificatePath);

        fs.writeFileSync(tempJsonPath, JSON.stringify(studentData));

        // Spawn Python process using the VENV python executable
        const pythonExecutable = path.resolve(__dirname, '../venv/bin/python3');
        const scriptPath = path.resolve(__dirname, '../scripts/generate_pdf.py');

        console.log(`Executing PDF generation: ${pythonExecutable} ${scriptPath} ${tempJsonPath}`);

        const pythonProcess = spawn(pythonExecutable, [
            scriptPath,
            tempJsonPath
        ]);

        let outputData = '';
        let errorData = '';

        pythonProcess.stdout.on('data', (data) => {
            outputData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });

        pythonProcess.on('close', (code) => {
            // Cleanup JSON
            try { fs.unlinkSync(tempJsonPath); } catch (e) { }

            if (code !== 0) {
                console.error('Python Script Error:', errorData);
                return res.status(500).json({ message: 'Error generating PDF', details: errorData });
            }

            const pdfPath = outputData.trim();
            if (fs.existsSync(pdfPath)) {
                res.download(pdfPath, `application_${student.firstName}_${student.lastName}.pdf`, (err) => {
                    if (err) console.error('Error downloading file:', err);
                });
            } else {
                console.error('PDF not found at path:', pdfPath);
                res.status(500).json({ message: 'PDF file was not generated.', details: outputData });
            }
        });

    } catch (error) {
        console.error('Error in export:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
};

// Delete student
exports.deleteStudent = async (req, res) => {
    try {
        const { id } = req.params;
        const student = await Student.findByPk(id);

        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        // Optional: Delete associated files if needed
        const deleteFile = (filePath) => {
            if (filePath && fs.existsSync(filePath)) {
                try {
                    fs.unlinkSync(filePath);
                } catch (e) {
                    console.error('Error deleting file:', filePath, e);
                }
            }
        };

        deleteFile(student.photoPath);
        deleteFile(student.transcriptPath);
        deleteFile(student.certificatePath);

        await student.destroy();
        res.status(200).json({ message: 'Student deleted successfully' });
    } catch (error) {
        console.error('Error deleting student:', error);
        res.status(500).json({ message: 'Error deleting student' });
    }
};
