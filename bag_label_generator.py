# bag_label_generator_v2.py
# 2" x 1" Thermal Labels with Aesthetic Design
# Left: Framed zone with Icon + "BAG #" + Variable Digits
# Right: QR Code zone (outside frame)
# Uses segno (QR) + svglib + reportlab

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from svglib.svglib import svg2rlg
import segno, io, pandas as pd
import os

# ----- Label Geometry (2" x 1") -----
# 1 inch = 25.4 mm
LABEL_W_MM = 50.8
LABEL_H_MM = 25.4
MARGIN_MM = 1.5  # Margin for the outer frame boundary

# Define the width of the left framed area (exactly half the label, 1 inch)
LEFT_FRAME_W_MM = 25.4

# ----- Layout Zones -----
# Right Zone for QR (Centered in the right 1" half)
QR_SIZE_MM = 20.0
# Start at 1 inch mark + half the remaining space
QR_X_MM = LEFT_FRAME_W_MM + ((LEFT_FRAME_W_MM - QR_SIZE_MM) / 2)
QR_Y_MM = (LABEL_H_MM - QR_SIZE_MM) / 2

# Left Zone Center (Center of the left 1" half)
CONTENT_CENTER_X_MM = LEFT_FRAME_W_MM / 2

# ----- Simple Tote Bag Icon SVG -----
TOTE_BAG_SVG = """<svg width="100" height="120" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 45 L80 45 L 75 95 Q 74 105 60 105 L 40 105 Q 26 105 25 95 L 20 45 Z" stroke="black" stroke-width="5" stroke-linejoin="round"/>
  <path d="M38 45 V 25 Q 38 20 43 20 H 57 Q 62 20 62 25 V 45" stroke="black" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="38" cy="50" r="3" fill="black"/>
  <circle cx="62" cy="50" r="3" fill="black"/>
</svg>"""

# ----- Data Source -----
DF_PATH = "production_bags.csv"
PDF_OUT = "production_bags_labels.pdf"


def draw_svg_content(canvas_obj, svg_string: str, x_mm: float, y_mm: float, size_mm: float):
    """Helper function to draw SVG data from a string onto the canvas centered at (x,y)."""
    buf = io.BytesIO(svg_string.encode('utf-8'))
    buf.seek(0)
    drawing = svg2rlg(buf)

    # Scale SVG to target size
    target_pts = size_mm * mm
    scale = target_pts / max(drawing.width, drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)

    # Draw centered on the given coordinates
    renderPDF.draw(drawing, canvas_obj, x_mm * mm - (drawing.width / 2), y_mm * mm - (drawing.height / 2))


def draw_qr_code(canvas_obj, data: str, x_mm: float, y_mm: float, size_mm: float):
    """Generates and draws the QR code SVG."""
    qr = segno.make(data, error='M')
    buf = io.BytesIO()
    qr.save(buf, kind="svg", border=0)
    svg_string = buf.getvalue().decode('utf-8')
    
    # Calculate center for the generic SVG drawer function
    center_x = x_mm + (size_mm / 2)
    center_y = y_mm + (size_mm / 2)
    draw_svg_content(canvas_obj, svg_string, center_x, center_y, size_mm)


def draw_aesthetic_content(c, bag_id: str):
    """Draws the frame (left side only), icon, and formatted text."""
    c.saveState()
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)

    # 1. Draw Rounded Frame (LEFT SIDE ONLY)
    # Width is limited to LEFT_FRAME_W_MM minus margins
    c.setLineWidth(1.5)
    c.roundRect(
        MARGIN_MM * mm,
        MARGIN_MM * mm,
        (LEFT_FRAME_W_MM - 2 * MARGIN_MM) * mm,
        (LABEL_H_MM - 2 * MARGIN_MM) * mm,
        3 * mm, # Corner radius
        stroke=1,
        fill=0
    )

    # 2. Draw Tote Bag Icon (Shifted UP away from text)
    ICON_SIZE_MM = 8.0
    ICON_Y_MM = 20.0 # Moved up from 18.0
    draw_svg_content(c, TOTE_BAG_SVG, CONTENT_CENTER_X_MM, ICON_Y_MM, ICON_SIZE_MM)

    # 3. Draw "BAG #" Label (Shifted DOWN slightly)
    c.setFont("Helvetica-Bold", 10)
    LABEL_Y_MM = 11.0 # Moved down from 12.0 to increase gap
    c.drawCentredString(CONTENT_CENTER_X_MM * mm, LABEL_Y_MM * mm, "BAG #")

    # 4. Draw the Variable Number (Large, Bold, shifted down with text)
    c.setFont("Helvetica-Bold", 24)
    VALUE_Y_MM = 4.0  # Moved down from 4.5
    c.drawCentredString(CONTENT_CENTER_X_MM * mm, VALUE_Y_MM * mm, bag_id)

    c.restoreState()


def main():
    # Create dummy data for demonstration if file doesn't exist
    if not os.path.exists(DF_PATH):
        print(f"{DF_PATH} not found. Creating dummy data for demonstration.")
        data = {
            "qr_data": [
                "SN:240213001ABC",
                "SN:240213002DEF",
                "SN:240213003GHI"
            ]
        }
        df = pd.DataFrame(data)
        df.to_csv(DF_PATH, index=False)
    else:
        df = pd.read_csv(DF_PATH, dtype={"qr_data": "string"})


    # Create Canvas
    c = canvas.Canvas(PDF_OUT, pagesize=(LABEL_W_MM * mm, LABEL_H_MM * mm))

    for _, row in df.iterrows():
        payload = str(row["qr_data"])
        
        # --- Data Extraction Logic (Adjust based on actual data format) ---
        # Extracting 3 digits starting from index 3 (e.g., after "SN:")
        clean_payload = payload.replace(" ", "")
        bag_id = clean_payload[11:14] 

        # 1. Draw Aesthetic Content (Left Side Frame & Data)
        draw_aesthetic_content(c, bag_id)

        # 2. Draw QR (Right Side, outside frame)
        draw_qr_code(
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