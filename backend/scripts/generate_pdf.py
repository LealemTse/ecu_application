import sys
import json
import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from pypdf import PdfWriter, PdfReader
from PIL import Image as PILImage

def generate_pdf(data_file):
    try:
        with open(data_file, 'r') as f:
            student = json.load(f)

        output_filename = f"temp/student_{student['id']}_export.pdf"
        
        # Margins
        doc = SimpleDocTemplate(output_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # --- Custom Styles (Times New Roman) ---
        styles['Normal'].fontName = 'Times-Roman'
        styles['Normal'].fontSize = 11
        
        styles['Heading1'].fontName = 'Times-Bold'
        styles['Heading1'].fontSize = 22
        styles['Heading1'].alignment = TA_CENTER
        styles['Heading1'].textColor = colors.HexColor('#0c1e33')
        
        styles['Heading2'].fontName = 'Times-Bold'
        styles['Heading2'].fontSize = 16
        styles['Heading2'].alignment = TA_CENTER
        styles['Heading2'].textColor = colors.HexColor('#495d72')
        
        styles['Heading3'].fontName = 'Times-Bold'
        styles['Heading3'].fontSize = 13
        styles['Heading3'].textColor = colors.HexColor('#0c1e33')
        styles['Heading3'].spaceBefore = 12
        styles['Heading3'].spaceAfter = 6
        styles['Heading3'].borderPadding = 4
        styles['Heading3'].backColor = colors.HexColor('#f4f5f7')

        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            borderWidth=0,
            borderColor=colors.HexColor('#0c1e33'),
            borderRadius=4
        )

        label_style = ParagraphStyle('Label', parent=styles['Normal'], fontName='Times-Bold')
        value_style = ParagraphStyle('Value', parent=styles['Normal'])

        story = []

        # --- Header Layout ---
        # Top Left: Student Photo
        # Top Right: Logo
        # Center: Text
        
        photo_cell = []
        if student.get('photoPath') and os.path.exists(student['photoPath']):
            try:
                img = Image(student['photoPath'])
                img.drawHeight = 1.6*inch
                img.drawWidth = 1.6*inch
                img.hAlign = 'LEFT'
                photo_cell.append(img)
            except Exception:
                photo_cell.append(Paragraph("[Photo]", styles['Normal']))
        else:
             photo_cell.append(Paragraph("[No Photo]", styles['Normal']))

        logo_cell = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, '../../frontend/images/imgecu2.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path)
                logo.drawHeight = 1.2*inch
                logo.drawWidth = 1.2*inch
                logo.hAlign = 'RIGHT'
                logo_cell.append(logo)
            except Exception:
                logo_cell.append(Paragraph("[Logo]", styles['Normal']))
        else:
            logo_cell.append(Paragraph("", styles['Normal']))

        title_text = f"""<font size=24><b>ECUSTA Higher Learning Institute</b></font><br/>
                        <font size=16 color="#495d72">Student Application Form</font><br/>
                        <font size=12>Application ID: {student.get('id', 'N/A')} | Status: {student.get('status', 'Pending').title()}</font>
                      """
        title_para = Paragraph(title_text, styles['Heading1'])

        # Header Table: Photo | Title | Logo
        header_table = Table([[photo_cell, title_para, logo_cell]], colWidths=[1.8*inch, 4.4*inch, 1.3*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph('<hr width="100%" color="#0c1e33" size="2"/>', styles['Normal']))
        story.append(Spacer(1, 15))


        # --- Helper for Data Tables ---
        def create_data_table(data_dict, col_widths=[2.5*inch, 5*inch]):
            rows = []
            for k, v in data_dict.items():
                label = Paragraph(k, label_style)
                value = Paragraph(str(v) if v is not None else "-", value_style)
                rows.append([label, value])
            
            if not rows: return None

            t = Table(rows, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), # Row striping? No, col background
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            return t

        # --- Personal Info ---
        story.append(Paragraph("Personal Profile", section_header_style))
        personal_data = {
            "First Name": student.get('firstName'),
            "Middle Name": student.get('middleName'),
            "Last Name": student.get('lastName'),
            "Date of Birth": student.get('dateOfBirth'),
            "Gender": student.get('gender', '').title(),
            "Nationality": student.get('nationality'),
            "Place of Birth": student.get('placeOfBirth'),
            "Marital Status": student.get('maritalStatus', '').title(),
            "Disabilities": student.get('disabilities', '').title(),
        }
        story.append(create_data_table(personal_data))
        
        # --- Address & Contact ---
        story.append(Paragraph("Address & Contact Details", section_header_style))
        address_data = {
            "Email": student.get('email'),
            "Phone Number": student.get('phoneNumber'),
            "Country": student.get('country'),
            "Region": student.get('region'),
            "City/Town": student.get('city'),
            "Sub City": student.get('subCity'),
            "Woreda": student.get('woreda'),
        }
        story.append(create_data_table(address_data))

        # --- Guardian Info ---
        story.append(Paragraph("Guardian / Contact Person", section_header_style))
        guardian_data = {
            "Full Name": student.get('guardianName'),
            "Mobile Number": student.get('guardianMobile'),
            "Phone Number": student.get('guardianPhone'),
            "Country": student.get('guardianCountry'),
            "Region": student.get('guardianRegion'),
            "City/Town": student.get('guardianCity'),
            "Sub City": student.get('guardianSubCity'),
            "Woreda": student.get('guardianWoreda'),
        }
        story.append(create_data_table(guardian_data))

        # --- Education ---
        story.append(Paragraph("Educational Background", section_header_style))
        
        # High School
        school_data = {
            "Main High School": student.get('highSchoolName'),
            "School Address": student.get('highSchoolAddress'),
            "Start Date": student.get('highSchoolStart'),
            "Completion Date": student.get('highSchoolEnd'),
        }
        story.append(create_data_table(school_data))
        story.append(Spacer(1, 5))

        # Additional Schools
        if student.get('additionalSchools') and isinstance(student['additionalSchools'], list):
            for i, school in enumerate(student['additionalSchools']):
                 add_school_data = {
                     f"Additional School {i+1}": school.get('name'),
                     "Address": school.get('address'),
                     "Start Date": school.get('start'),
                     "Completion Date": school.get('end'),
                 }
                 story.append(create_data_table(add_school_data))
                 story.append(Spacer(1, 5))

        # --- Grade 12 Results ---
        story.append(Paragraph("Grade 12 / EHEECE Results", section_header_style))
        
        # Stream & Total
        meta_results = {
            "Science Stream": student.get('scienceStream', '').title(),
            "Exam Year": student.get('examYear'),
            "Total Score": student.get('totalScore'),
            "Chosen Field of Study": student.get('fieldOfStudy'),
        }
        story.append(create_data_table(meta_results))
        story.append(Spacer(1, 10))

        # Subject Scores Table
        subjects_data = []
        subjects_data.append([Paragraph("<b>Subject</b>", label_style), Paragraph("<b>Score</b>", label_style)])
        
        for i in range(1, 8):
            subj = student.get(f'resultSubject{i}')
            score = student.get(f'resultScore{i}')
            if subj or score:
                subjects_data.append([Paragraph(str(subj), value_style), Paragraph(str(score), value_style)])
        
        if len(subjects_data) > 1:
            t_scores = Table(subjects_data, colWidths=[3.75*inch, 3.75*inch])
            t_scores.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e1e5eb')), # Header row
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (1,1), (1,-1), 'CENTER'), # Center scores
            ]))
            story.append(Paragraph("<b>Detailed Subject Results</b>", ParagraphStyle('SubHeader', parent=styles['Normal'], spaceAfter=5)))
            story.append(t_scores)

        doc.build(story)

        # --- Merge Attachments ---
        merger = PdfWriter()
        
        with open(output_filename, "rb") as f:
            merger.append(f)

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

        print(final_output)

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
