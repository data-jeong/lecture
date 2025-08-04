import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from datetime import datetime


class ExcelExporter:
    """Export data to Excel format"""
    
    @staticmethod
    def export_grades(data: pd.DataFrame, filename: str,
                     sheet_name: str = "Grades") -> str:
        """Export grades DataFrame to Excel"""
        output_path = Path(filename)
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the worksheet
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                        
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        return str(output_path)
        
    @staticmethod
    def export_transcript(transcript_data: Dict[str, Any], filename: str) -> str:
        """Export transcript to Excel with multiple sheets"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Student info sheet
            student_df = pd.DataFrame([transcript_data["student_info"]])
            student_df.to_excel(writer, sheet_name="Student Info", index=False)
            
            # Grade history sheet
            if transcript_data.get("grade_history"):
                history_df = pd.DataFrame(transcript_data["grade_history"])
                history_df.to_excel(writer, sheet_name="Grade History", index=False)
                
            # Semester GPAs sheet
            if transcript_data.get("semester_gpas"):
                gpa_df = pd.DataFrame(transcript_data["semester_gpas"])
                gpa_df.to_excel(writer, sheet_name="Semester GPAs", index=False)
                
        return str(output_path)
        
    @staticmethod
    def export_statistics(stats_data: Dict[str, Any], filename: str) -> str:
        """Export statistics report to Excel"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Overall statistics
            overall_df = pd.DataFrame([stats_data["overall"]])
            overall_df.to_excel(writer, sheet_name="Overall", index=False)
            
            # Department statistics
            if stats_data.get("department_statistics"):
                dept_df = pd.DataFrame(stats_data["department_statistics"])
                dept_df.to_excel(writer, sheet_name="Departments", index=False)
                
            # Course statistics
            if stats_data.get("course_statistics"):
                course_df = pd.DataFrame(stats_data["course_statistics"])
                course_df.to_excel(writer, sheet_name="Courses", index=False)
                
            # Top students
            if stats_data.get("top_students"):
                top_df = pd.DataFrame(stats_data["top_students"])
                top_df.to_excel(writer, sheet_name="Top Students", index=False)
                
        return str(output_path)


class PDFExporter:
    """Export data to PDF format (simplified implementation)"""
    
    @staticmethod
    def export_transcript(transcript_data: Dict[str, Any], filename: str) -> str:
        """Export transcript to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            elements.append(Paragraph("Academic Transcript", title_style))
            elements.append(Spacer(1, 20))
            
            # Student Information
            student_info = transcript_data["student_info"]
            info_data = [
                ["Student ID:", student_info["student_id"]],
                ["Name:", student_info["name"]],
                ["Email:", student_info["email"] or "N/A"],
                ["Major:", student_info["major"] or "N/A"],
                ["Status:", student_info["status"]],
                ["Overall GPA:", str(student_info["overall_gpa"])],
                ["Total Credits:", str(student_info["total_credits"])]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 30))
            
            # Grade History
            elements.append(Paragraph("Grade History", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            if transcript_data.get("grade_history"):
                # Create header
                grade_headers = ["Semester", "Course", "Credits", "Grade", "Points", "Score"]
                grade_data = [grade_headers]
                
                # Add grade records
                for record in transcript_data["grade_history"]:
                    grade_data.append([
                        f"{record['year']}-{record['semester']}",
                        f"{record['course_code']} {record['course_name'][:20]}",
                        str(record.get('credits', '')),
                        record.get('letter_grade', ''),
                        str(record.get('grade_points', '')),
                        str(record.get('total_score', ''))
                    ])
                    
                grade_table = Table(grade_data)
                grade_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(grade_table)
                
            # Build PDF
            doc.build(elements)
            
            return str(output_path)
            
        except ImportError:
            # Fallback if reportlab is not installed
            return PDFExporter._export_transcript_text(transcript_data, filename)
            
    @staticmethod
    def _export_transcript_text(transcript_data: Dict[str, Any], filename: str) -> str:
        """Export transcript as text file (fallback)"""
        output_path = Path(filename).with_suffix('.txt')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ACADEMIC TRANSCRIPT\n")
            f.write("=" * 60 + "\n\n")
            
            # Student info
            student_info = transcript_data["student_info"]
            f.write("STUDENT INFORMATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Student ID: {student_info['student_id']}\n")
            f.write(f"Name: {student_info['name']}\n")
            f.write(f"Email: {student_info['email'] or 'N/A'}\n")
            f.write(f"Major: {student_info['major'] or 'N/A'}\n")
            f.write(f"Status: {student_info['status']}\n")
            f.write(f"Overall GPA: {student_info['overall_gpa']}\n")
            f.write(f"Total Credits: {student_info['total_credits']}\n")
            f.write("\n")
            
            # Grade history
            f.write("GRADE HISTORY\n")
            f.write("-" * 30 + "\n")
            
            if transcript_data.get("grade_history"):
                for record in transcript_data["grade_history"]:
                    f.write(f"\n{record['year']}-{record['semester']}:\n")
                    f.write(f"  {record['course_code']} - {record['course_name']}\n")
                    f.write(f"  Credits: {record.get('credits', 'N/A')}\n")
                    f.write(f"  Grade: {record.get('letter_grade', 'N/A')}\n")
                    f.write(f"  Score: {record.get('total_score', 'N/A')}\n")
                    
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        return str(output_path)
        
    @staticmethod
    def export_grade_report(grade_df: pd.DataFrame, filename: str,
                          title: str = "Grade Report") -> str:
        """Export grade report to PDF"""
        # For simplicity, export as formatted text
        output_path = Path(filename).with_suffix('.txt')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"{title.upper()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write DataFrame as formatted text
            f.write(grade_df.to_string(index=False))
            
            f.write("\n\n" + "=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        return str(output_path)


class CSVExporter:
    """Export data to CSV format"""
    
    @staticmethod
    def export_data(data: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to CSV"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data.to_csv(output_path, index=False)
        
        return str(output_path)
        
    @staticmethod
    def export_grades(grades: List[Dict[str, Any]], filename: str) -> str:
        """Export grades list to CSV"""
        df = pd.DataFrame(grades)
        return CSVExporter.export_data(df, filename)


class JSONExporter:
    """Export data to JSON format"""
    
    @staticmethod
    def export_data(data: Any, filename: str, indent: int = 2) -> str:
        """Export data to JSON"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
            
        return str(output_path)