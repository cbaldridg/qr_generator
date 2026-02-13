# bag_label_generator.py
# 2" x 1" Thermal Labels
# Left: "Bag #" + Variable Digits | Right: QR Code
# Uses segno (QR) + svglib + reportlab

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import segno, io, pandas as pd

# ----- Label Geometry (2" x 1") -----
# 1 inch = 25.4 mm
LABEL_W_MM = 50.8
LABEL_H_MM = 25.4

# ----- Layout Zones -----
# We split the label roughly in half
# Left Zone: 0 to 25mm (Text)
# Right Zone: 25mm to 50mm (QR)

# QR Settings
QR_SIZE_MM = 20.0  # Approx 0.8 inches, fits nicely in the 1" height
# Position QR centered in the right half of the label
QR_X_MM = 25.4 + ((25.4 - QR_SIZE_MM) / 2) 
QR_Y_MM = (LABEL_H_MM - QR_SIZE_MM) / 2

# Text Settings
TEXT_CENTER_X_MM = 12.7  # Center of the left half (1 inch / 2)
TEXT_LABEL_Y_MM = 15.0   # Y position for "Bag #"
TEXT_VALUE_Y_MM = 6.0    # Y position for the big number

# ----- Data Source -----
# Assuming same format as before
DF_PATH = "production_bags.csv"
PDF_OUT = "bag_labels.pdf"

def draw_qr_svg(canvas_obj, data: str, x_mm: float, y_mm: float, size_mm: float):
    # Standard QR generation (no overlay needed)
    qr = segno.make(data, error='M') # 'M' is standard balance
    buf = io.BytesIO()
    qr.save(buf, kind="svg", border=0)
    buf.seek(0)

    drawing = svg2rlg(buf)
    
    # Scale SVG to target size
    target_pts = size_mm * mm
    scale = target_pts / max(drawing.width, drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)

    renderPDF.draw(drawing, canvas_obj, x_mm * mm, y_mm * mm)

def draw_text_content(c, bag_id: str):
    c.saveState()
    c.setFillColor("black")
    
    # 1. Draw "Bag #" Label
    c.setFont("Helvetica", 18)
    c.drawCentredString(TEXT_CENTER_X_MM * mm, TEXT_LABEL_Y_MM * mm, "BAG #")
    
    # 2. Draw the Variable Number (Large, Bold)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(TEXT_CENTER_X_MM * mm, TEXT_VALUE_Y_MM * mm, bag_id)
    
    c.restoreState()

def main():
    try:
        # Load data
        df = pd.read_csv(DF_PATH, dtype={"qr_data": "string"})
    except FileNotFoundError:
        print(f"Error: {DF_PATH} not found.")
        return

    # Create Canvas
    c = canvas.Canvas(PDF_OUT, pagesize=(LABEL_W_MM * mm, LABEL_H_MM * mm))

    for _, row in df.iterrows():
        payload = str(row["qr_data"])
        
        # --- Data Extraction Logic ---
        # "extract the first 3 digits of the current SN"
        # Assuming the 'SN' starts at the beginning of the payload after stripping spaces.
        # If your SN is buried in the middle (like previous scripts), change the slice below.
        
        clean_payload = payload.replace(" ", "")
        
        # EXTRACT: First 3 digits of SN
        bag_id = clean_payload[11:14] 

        # 1. Draw Text (Left Side)
        draw_text_content(c, bag_id)

        # 2. Draw QR (Right Side)
        draw_qr_svg(
            canvas_obj=c,
            data=payload,
            x_mm=QR_X_MM,
            y_mm=QR_Y_MM,
            size_mm=QR_SIZE_MM
        )

        c.showPage()

    c.save()
    print(f"Successfully generated {PDF_OUT}")

if __name__ == "__main__":
    main()