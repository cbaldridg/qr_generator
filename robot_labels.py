# qr_generator_robots.py
# 1x1 inch labels with Center-Embedded Text
# Uses segno (QR) + svglib + reportlab

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import segno, io, pandas as pd

# ----- Label & QR geometry (in mm) -----
# 1 inch = 25.4 mm
LABEL_W_MM, LABEL_H_MM = 25.4, 25.4   
QR_SIZE_MM = 22.0                      # Leaves ~1.7mm margin on sides

# Center the QR code on the 1x1 label
QR_X_MM = (LABEL_W_MM - QR_SIZE_MM) / 2
QR_Y_MM = (LABEL_H_MM - QR_SIZE_MM) / 2

# ----- Overlay Settings -----
# The box size must be small enough not to break the QR, 
# but large enough to fit text. ~20-25% of QR size is usually safe with 'H' level.
OVERLAY_SIZE_MM = 3.5 
FONT_SIZE = 10 

# ----- Data source -----
DF_PATH = "robot_serials.csv"
PDF_OUT = "robot_labels.pdf"

# --- Border settings (Optional, mostly for visual debugging on white paper) ---
BORDER_RADIUS_MM = 1.0
BORDER_LINE_WIDTH_PT = 0.5
BORDER_INSET_MM = (BORDER_LINE_WIDTH_PT / 2.0) / mm

def draw_label_border(c, label_w_mm: float, label_h_mm: float):
    c.saveState()
    c.setLineWidth(BORDER_LINE_WIDTH_PT)
    c.setStrokeColorRGB(0.8, 0.8, 0.8) # Light grey border so it doesn't distract
    x = BORDER_INSET_MM
    y = BORDER_INSET_MM
    w = label_w_mm - 2 * BORDER_INSET_MM
    h = label_h_mm - 2 * BORDER_INSET_MM
    c.roundRect(x * mm, y * mm, w * mm, h * mm, BORDER_RADIUS_MM * mm, stroke=1, fill=0)
    c.restoreState()

def draw_qr_svg(canvas_obj, data: str, x_mm: float, y_mm: float, size_mm: float, error_level: str = "H"):
    # error='H' (High) is CRITICAL here. It allows up to 30% of the code to be covered/damaged.
    qr = segno.make(data, error=error_level)
    buf = io.BytesIO()
    
    # border=0 because we are positioning it manually and don't want extra whitespace
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

def draw_center_overlay(c, text: str, label_w_mm, label_h_mm):
    """Draws a white box with text in the absolute center of the label."""
    c.saveState()
    
    # 1. Calculate Center positions
    center_x = (label_w_mm / 2) * mm
    center_y = (label_h_mm / 2) * mm
    half_box = (OVERLAY_SIZE_MM / 2) * mm
    
    # 2. Draw White Background Box (covers the QR pixels)
    c.setFillColor("white")
    c.setStrokeColor("white") # Stroke matching fill ensures no hairline gaps
    # Draw rect centered
    c.rect(center_x - half_box, center_y - half_box, OVERLAY_SIZE_MM * mm, OVERLAY_SIZE_MM * mm, fill=1, stroke=1)
    
    # 3. Draw Text
    c.setFillColor("black")
    c.setFont("Helvetica-Bold", FONT_SIZE)
    # vertically center text roughly by adjusting y down by half font height (approx)
    # precise vertical centering in PDF is tricky, usually 0.35 * font_size correction works well
    text_y_adj = (FONT_SIZE * 0.35) 
    
    c.drawCentredString(center_x, center_y - text_y_adj, text)
    
    c.restoreState()

def main():
    try:
        df = pd.read_csv(DF_PATH, dtype={"qr_data": "string"})
    except FileNotFoundError:
        print(f"Error: {DF_PATH} not found. Please create a dummy CSV to test.")
        return

    c = canvas.Canvas(PDF_OUT, pagesize=(LABEL_W_MM * mm, LABEL_H_MM * mm))

    for _, row in df.iterrows():
        payload = str(row["qr_data"])
        
        # 1. Extract Digits
        # Remove spaces
        stripped_payload = payload.replace(" ", "")
        

        try:
            robot_sn = stripped_payload[12:14]  # 0-based index, so 12 and 13 are the 13th and 14th characters
            #print(robot_sn)  # Debug: Print extracted SN to verify correctness
        except IndexError:
            robot_sn = "??"
            print(f"Warning: Payload too short for SN extraction: {payload}")

        # 2. Draw the QR code (High Error Correction)
        draw_qr_svg(
            canvas_obj=c,
            data=payload,
            x_mm=QR_X_MM,
            y_mm=QR_Y_MM,
            size_mm=QR_SIZE_MM,
            error_level="H" 
        )

        # 3. Draw the Center Overlay
        draw_center_overlay(c, robot_sn, LABEL_W_MM, LABEL_H_MM)

        # 4. Draw Label Border (optional)
        #draw_label_border(c, LABEL_W_MM, LABEL_H_MM)

        c.showPage()

    c.save()
    print(f"Successfully generated {PDF_OUT}")

if __name__ == "__main__":
    main()