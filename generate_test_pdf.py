from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1: Text
    c.drawString(100, 750, "This is a test document with selectable text.")
    c.drawString(100, 730, "It should be extracted by PyPDF2.")
    c.showPage()
    
    # Page 2: Text again (simulating multi-page)
    c.drawString(100, 750, "This is page 2.")
    c.showPage()
    
    c.save()

if __name__ == "__main__":
    create_pdf("test_doc.pdf")
