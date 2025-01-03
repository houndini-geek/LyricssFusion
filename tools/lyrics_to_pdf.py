from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog, messagebox

def export_to_pdf(artist, track, lyrics):
    # Ask user where to save the PDF
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save Lyrics as PDF"
    )
    
    if not save_path:
        return  # User canceled save dialog
    
    try:
        # Create PDF
        pdf = canvas.Canvas(save_path, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        
        # Add metadata
        pdf.drawString(30, 750, f"Song: {track}")
        pdf.drawString(30, 735, f"Artist: {artist}")
        pdf.drawString(30, 720, "Source: LyricsFusion")
        
        # Add lyrics
        y_position = 700
        for line in lyrics.split("\n"):
            if y_position < 50:  # Add a new page if content overflows
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750
            pdf.drawString(30, y_position, line)
            y_position -= 15
        
        pdf.save()  # Save the PDF
        messagebox.showinfo("Success", "Lyrics exported as PDF successfully!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF: {e}")
