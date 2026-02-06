import sys
import json
import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pypdf import PdfWriter, PdfReader
from PIL import Image as PILImage

def generate_pdf(data_file):
    try:
        with open(data_file, 'r') as f:
            student = json.load(f)

        output_filename = f"temp/student_{student['id']}_export.pdf"
        
        # Create the main document with student details
        doc = SimpleDocTemplate(output_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # --- Update Styles to use Times New Roman ---
        styles['Normal'].fontName = 'Times-Roman'
        styles['Normal'].fontSize = 11
        
        styles['Heading1'].fontName = 'Times-Bold'
        styles['Heading1'].fontSize = 20
        styles['Heading1'].alignment = TA_CENTER
        
        styles['Heading2'].fontName = 'Times-Bold'
        styles['Heading2'].fontSize = 16
        styles['Heading2'].alignment = TA_CENTER
        
        styles['Heading3'].fontName = 'Times-Bold'
        styles['Heading3'].fontSize = 13
        styles['Heading3'].textColor = colors.HexColor('#0c1e33')
        styles['Heading3'].spaceBefore = 10
        styles['Heading3'].spaceAfter = 6

        story = []

        # --- Header with Logo and ID ---
        # Path relative to this script: ../../frontend/images/imgecu2.png
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, '../../frontend/images/imgecu2.png')
        
        header_content = []
        
        # Logo and ID Column
        left_col = []
        if os.path.exists(logo_path):
            try:
                # Resize logo to fit nicely, maintain aspect ratio roughly or strictly
                # Let's assume a width of 1.5 inch
                img = Image(logo_path)
                img.drawHeight = 1.2 * inch
                img.drawWidth = 1.2 * inch # Approximate, better to let it scale if proportional
                img.hAlign = 'LEFT'
                left_col.append(img)
            except Exception as e:
                left_col.append(Paragraph("Logo Error", styles['Normal']))
        else:
             left_col.append(Paragraph("[Logo Not Found]", styles['Normal']))

        left_col.append(Spacer(1, 6))
        left_col.append(Paragraph(f"<b>ID: {student.get('id', 'N/A')}</b>", styles['Normal']))

        # specific style for main title to align with logo
        title_text = f"""<font size=20><b>ECUSTA Higher Learning Institute</b></font><br/>
                        <font size=16>Student Application Form</font>
                      """
        
        title_para = Paragraph(title_text, styles['Heading1'])

        # Create Header Table
        # Col 1: Logo & ID (Width ~ 1.5 inch), Col 2: Title (Rest)
        header_table = Table([[left_col, title_para]], colWidths=[2*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))


        # --- Photo (Top Right of Body or separate section? User didn't specify, keeping it regular) ---
        if student.get('photoPath'):
            photo_path = student['photoPath']
            if os.path.exists(photo_path):
                try:
                    img = Image(photo_path)
                    img.drawHeight = 2.0*inch
                    img.drawWidth = 2.0*inch
                    img.hAlign = 'RIGHT'
                    story.append(img)
                    story.append(Spacer(1, 6))
                except Exception as e:
                    pass

        # --- Details Section Helper ---
        def add_section(title, data_dict):
            story.append(Paragraph(title, styles['Heading3']))
            table_data = []
            for k, v in data_dict.items():
                # Format key to be bold Times-Roman
                key_para = Paragraph(f"<b>{k}:</b>", styles['Normal'])
                val_para = Paragraph(str(v) if v is not None else "N/A", styles['Normal'])
                table_data.append([key_para, val_para])
            
            if table_data:
                t = Table(table_data, colWidths=[2.5*inch, 4.5*inch])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                    ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                    ('PADDING', (0,0), (-1,-1), 6),
                    ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))

        # Personal Info
        add_section("Personal Information", {
            "Full Name": f"{student.get('firstName', '')} {student.get('middleName', '')} {student.get('lastName', '')}",
            "Date of Birth": student.get('dateOfBirth'),
            "Gender": student.get('gender'),
            "Nationality": student.get('nationality'),
            "Place of Birth": student.get('placeOfBirth'),
            "Marital Status": student.get('maritalStatus'),
            "Disabilities": student.get('disabilities'),
            "Student ID": student.get('id'),
            "Status": student.get('status')
        })

        # Address
        add_section("Address Information", {
            "Country": student.get('country'),
            "Region": student.get('region'),
            "City": student.get('city'),
            "Sub City": student.get('subCity'),
            "Woreda": student.get('woreda')
        })

        # Contact
        add_section("Contact Information", {
            "Email": student.get('email'),
            "Phone Number": student.get('phoneNumber')
        })

        # Guardian
        add_section("Guardian Information", {
            "Guardian Name": student.get('guardianName'),
            "Guardian Mobile": student.get('guardianMobile'),
            "Guardian Phone": student.get('guardianPhone'),
            "Guardian City": student.get('guardianCity')
        })

        # Academic
        add_section("Academic Profile", {
            "High School Name": student.get('highSchoolName'),
            "High School Address": student.get('highSchoolAddress'),
            "Science Stream": student.get('scienceStream'),
            "Grade 12 Total Score": student.get('totalScore'),
            "Exam Year": student.get('examYear'),
            "Field of Study Choice": student.get('fieldOfStudy')
        })

        # Additional Schools
        if student.get('additionalSchools') and isinstance(student['additionalSchools'], list):
             story.append(Paragraph("Additional High Schools", styles['Heading3']))
             for i, school in enumerate(student['additionalSchools']):
                 school_data = {
                     f"School {i+1} Name": school.get('name'),
                     "Address": school.get('address'),
                     "Start Date": school.get('start'),
                     "End Date": school.get('end')
                 }
                 add_section(f"High School {i+1}", school_data)


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
                elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    # Convert image to PDF page
                    try:
                        img_temp_pdf = path + ".temp.pdf"
                        img = PILImage.open(path)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(img_temp_pdf)
                        with open(img_temp_pdf, "rb") as f:
                            merger.append(f)
                    except Exception as e:
                         print(f"Warning: Could not merge Image {path}: {e}", file=sys.stderr)

        final_output = f"temp/student_{student['id']}_final.pdf"
        merger.write(final_output)
        merger.close()

        print(final_output) # Print final path for Node.js to read

    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py <data_json_file>")
        sys.exit(1)
    
    generate_pdf(sys.argv[1])
