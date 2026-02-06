import sys
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pypdf import PdfWriter, PdfReader
from PIL import Image as PILImage

def generate_pdf(data_file):
    try:
        with open(data_file, 'r') as f:
            student = json.load(f)

        output_filename = f"temp/student_{student['id']}_export.pdf"
        
        # Create the main document with student details
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # --- Header ---
        # Logo (if exists) - defaulting to text if no logo file found
        # story.append(Image('config/logo.png', width=2*inch, height=1*inch)) # Example
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=1, # Center
            spaceAfter=20,
            textColor=colors.HexColor('#0c1e33')
        )
        story.append(Paragraph("ECUSTA Higher Learning Institute", title_style))
        story.append(Paragraph("Student Application Form", styles['Heading2']))
        story.append(Spacer(1, 12))

        # --- Photo ---
        if student.get('photoPath'):
            photo_path = student['photoPath']
            if os.path.exists(photo_path):
                # Resize keeping aspect ratio
                img = Image(photo_path)
                img.drawHeight = 2.0*inch
                img.drawWidth = 2.0*inch
                # img.hAlign = 'RIGHT'
                story.append(img)
                story.append(Spacer(1, 12))

        # --- Details ---
        
        def add_section(title, data_dict):
            story.append(Paragraph(title, styles['Heading3']))
            table_data = []
            for k, v in data_dict.items():
                if v:
                    table_data.append([Paragraph(f"<b>{k}:</b>", styles['Normal']), Paragraph(str(v), styles['Normal'])])
            
            if table_data:
                t = Table(table_data, colWidths=[2.5*inch, 4.5*inch])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                    ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))

        # Personal Info
        add_section("Personal Information", {
            "Full Name": f"{student.get('firstName', '')} {student.get('middleName', '')} {student.get('lastName', '')}",
            "Date of Birth": student.get('dateOfBirth'),
            "Gender": student.get('gender'),
            "Nationality": student.get('nationality'),
            "Place of Birth": student.get('placeOfBirth'),
            "Marital Status": student.get('maritalStatus'),
            "Disabilities": student.get('disabilities')
        })

        # Address
        add_section("Address", {
            "Country": student.get('country'),
            "Region": student.get('region'),
            "City": student.get('city'),
            "Sub City": student.get('subCity'),
            "Woreda": student.get('woreda')
        })

        # Contact
        add_section("Contact", {
            "Email": student.get('email'),
            "Phone Number": student.get('phoneNumber')
        })

        # Guardian
        add_section("Guardian Information", {
            "Name": student.get('guardianName'),
            "Mobile": student.get('guardianMobile'),
            "Phone": student.get('guardianPhone'),
            "City": student.get('guardianCity')
        })

        # Academic
        add_section("Academic Profile", {
            "High School": student.get('highSchoolName'),
            "Address": student.get('highSchoolAddress'),
            "Stream": student.get('scienceStream'),
            "Grade 12 Score": student.get('totalScore'),
            "Exam Year": student.get('examYear'),
            "Field of Study": student.get('fieldOfStudy')
        })

        # Additional Schools
        if student.get('additionalSchools') and isinstance(student['additionalSchools'], list):
             story.append(Paragraph("Additional High Schools", styles['Heading3']))
             for i, school in enumerate(student['additionalSchools']):
                 school_data = [
                     [f"School {i+1}", school.get('name', 'N/A')],
                     ["Address", school.get('address', 'N/A')],
                     ["Start", school.get('start', 'N/A')],
                     ["End", school.get('end', 'N/A')]
                 ]
                 t = Table(school_data, colWidths=[2.5*inch, 4.5*inch])
                 t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                 ]))
                 story.append(t)
                 story.append(Spacer(1, 5))


        doc.build(story)

        # --- Merge Attachments (Transcript, Certificate) ---
        merger = PdfWriter()
        
        # Add generated details page
        with open(output_filename, "rb") as f:
            merger.append(f)

        # Attachments
        attachments = []
        if student.get('transcriptPath'): attachments.append(student['transcriptPath'])
        if student.get('certificatePath'): attachments.append(student['certificatePath'])

        for path in attachments:
            if os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                if ext == '.pdf':
                    try:
                        with open(path, "rb") as f:
                            merger.append(f)
                    except Exception as e:
                        print(f"Warning: Could not merge PDF {path}: {e}", file=sys.stderr)
                elif ext in ['.jpg', '.jpeg', '.png']:
                    # Convert image to PDF page
                    try:
                        img_temp_pdf = path + ".temp.pdf"
                        img = PILImage.open(path)
                        img = img.convert('RGB')
                        img.save(img_temp_pdf)
                        with open(img_temp_pdf, "rb") as f:
                            merger.append(f)
                        # os.remove(img_temp_pdf) # Clean up later
                    except Exception as e:
                         print(f"Warning: Could not merge Image {path}: {e}", file=sys.stderr)

        final_output = f"temp/student_{student['id']}_final.pdf"
        merger.write(final_output)
        merger.close()

        print(final_output) # Print final path for Node.js to read

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py <data_json_file>")
        sys.exit(1)
    
    generate_pdf(sys.argv[1])
