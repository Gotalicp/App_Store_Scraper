import pandas as pd
import os
import re
from fpdf import FPDF
import unidecode

# Path to your Excel file
excel_file = 'apps.xlsx'

def sanitize_filename(sheet_name):
    # Sanitize the filename to remove unsupported characters
    return re.sub(r'[\\/*?:"<>|]', "_", sheet_name)

def safe_text(text):
    # Check if the text is NaN or None, and if so, return an empty string
    if pd.isna(text):
        return ''
    # Convert text to ASCII and remove unsupported characters
    return unidecode.unidecode(str(text))

columns_to_extract = ['user', 'review', 'rating']

output_folder = 'reviews'
os.makedirs(output_folder, exist_ok=True)

xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names[1:]

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'App Reviews', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, safe_text(title), 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, safe_text(body))
        self.ln()

    def add_review(self, user, review, rating):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'User: {safe_text(user)}', 0, 1, 'L')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Rating: {safe_text(rating)}', 0, 1, 'L')
        self.multi_cell(0, 10, f'Review: {safe_text(review)}')
        self.ln(10)

for sheet_name in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=columns_to_extract)
    
    if df.empty:
        print(f"Skipping empty sheet: {sheet_name}")
        continue
    
    sanitized_sheet_name = sanitize_filename(sheet_name)
    
    output_file = os.path.join(output_folder, f"{sanitized_sheet_name}.pdf")
    
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title(f'Reviews for {sheet_name}')
    
    for index, row in df.iterrows():
        pdf.add_review(row['user'], row['review'], row['rating'])
    
    pdf.output(output_file)
    print(f"Processed sheet: {sheet_name}")
