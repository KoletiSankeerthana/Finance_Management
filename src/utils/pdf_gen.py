from fpdf import FPDF
from datetime import datetime
import re
import os
from src.utils.formatting import format_currency

class StrategicReportPDF(FPDF):
    def __init__(self, period_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period_text = period_text

    def header(self):
        # Professional Heading
        self.set_font('DejaVu', 'B', 16)
        self.set_text_color(0, 128, 128) # Teal
        self.cell(0, 12, 'EXPENSE TRACKER - STRATEGIC REPORT', 0, 1, 'C')
        
        # Metadata
        self.set_font('DejaVu', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, f'Analysis Period: {self.period_text}', 0, 1, 'C')
        self.cell(0, 6, f'Generated On: {datetime.now().strftime("%d %b %Y, %H:%M")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def safe_encode(text):
    """Clean text for standard PDF rendering while preserving essential characters."""
    if not text: return ""
    # Strip emojis and non-standard symbols that might crash the font
    return re.sub(r'[^\x00-\x7F\u20B9]+', '', str(text)).strip()

def generate_expense_pdf(df, total_amount):
    # Determine date range for header
    p_text = "Detailed Records"
    if not df.empty:
        start_date = df['date'].min().strftime('%d %b %Y')
        end_date = df['date'].max().strftime('%d %b %Y')
        p_text = f"{start_date} - {end_date}"

    pdf = StrategicReportPDF(p_text)
    
    # --- Universal Font Resolution ---
    # Attempt to load DejaVuSans for Rupee (₹) Support
    font_paths = [
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "src/assets/fonts/DejaVuSans.ttf",
        "DejaVuSans.ttf"
    ]
    
    target_font = None
    for path in font_paths:
        if os.path.exists(path):
            target_font = path
            break
            
    # Fallback to Arial if DejaVu is missing (Windows Unicode support)
    if not target_font and os.path.exists("C:\\Windows\\Fonts\\arial.ttf"):
        target_font = "C:\\Windows\\Fonts\\arial.ttf"

    if target_font:
        # fpdf2 uses add_font(family, style, fname)
        # Unicode is handled natively
        pdf.add_font('DejaVu', '', target_font)
        # Attempt to find Bold variant
        bold_candidate = target_font.replace('.ttf', '-Bold.ttf').replace('arial.ttf', 'arialbd.ttf')
        if os.path.exists(bold_candidate):
            pdf.add_font('DejaVu', 'B', bold_candidate)
        else:
            pdf.add_font('DejaVu', 'B', target_font)
    else:
        # Emergency Fallback to core font (No Rupee support)
        pdf.add_font('DejaVu', '', 'helvetica')
        pdf.add_font('DejaVu', 'B', 'helvetica-bold')

    pdf.add_page()
    
    # Table Header Design
    pdf.set_fill_color(0, 128, 128) # Teal
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('DejaVu', 'B', 10)
    
    # Columns: Date, Category, Payment Mode, Amount, Description
    pdf.cell(25, 10, ' Date', 1, 0, 'L', True)
    pdf.cell(40, 10, ' Category', 1, 0, 'L', True)
    pdf.cell(30, 10, ' Mode', 1, 0, 'L', True)
    pdf.cell(35, 10, ' Amount', 1, 0, 'C', True)
    pdf.cell(60, 10, ' Description', 1, 1, 'L', True)

    # Table Content
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('DejaVu', '', 9)
    
    for _, row in df.sort_values('date', ascending=True).iterrows():
        pdf.cell(25, 8, f' {row["date"].strftime("%d/%m/%Y")}', 1)
        
        # Category (Strip Emoji)
        raw_cat = str(row['category'])
        clean_cat = safe_encode(raw_cat.split(' ', 1)[1] if ' ' in raw_cat else raw_cat)
        pdf.cell(40, 8, f' {clean_cat}', 1)
        
        pdf.cell(30, 8, f' {row["payment_method"]}', 1)
        
        # Use format_currency which includes ₹ symbol
        pdf.cell(35, 8, f'{format_currency(row["amount"])} ', 1, 0, 'R')
        
        # Description
        desc_text = safe_encode(row['notes'])
        pdf.cell(60, 8, f' {desc_text[:35]}', 1, 1)

    # Final Summary Row
    pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.set_text_color(0, 128, 128)
    pdf.cell(130, 10, 'TOTAL CUMULATIVE EXPENDITURE:', 0, 0, 'R')
    pdf.cell(35, 10, f'{format_currency(total_amount)}', 0, 1, 'R')

    return pdf.output()
