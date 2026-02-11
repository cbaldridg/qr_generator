# qr_generator_vector.py
# PDF labels with vector (SVG) QR codes via segno + svglib + reportlab

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import segno, io, pandas as pd

# ----- Label & QR geometry (in mm) -----
LABEL_W_MM, LABEL_H_MM = 76, 102          # physical label size
QR_SIZE_MM = 25                            # final printed edge length of QR

# Place QR centered at X=43 mm, vertically centered
# (Note: X and Y are relative to the PDF bottom-left origin)
QR_X_MM = 43 - (QR_SIZE_MM / 2)
QR_Y_MM = (LABEL_H_MM / 2) - (QR_SIZE_MM / 2)
QR_CENTER_Y_MM = LABEL_H_MM / 2

# Text positioning (Left of QR in PDF = "Above" when rotated)
TEXT_GAP_MM = 2.0  
# This X coordinate will be the baseline for the rotated text
TEXT_X_MM = QR_X_MM - TEXT_GAP_MM 

# ----- Data source -----
DF_PATH = "production_totes.csv"

# ----- PDF out -----
PDF_OUT = "labels.pdf"

# --- Border settings ---
BORDER_RADIUS_MM = 2.0
BORDER_LINE_WIDTH_PT = 0.5
BORDER_INSET_MM = (BORDER_LINE_WIDTH_PT / 2.0) / mm

def draw_label_border(c, label_w_mm: float, label_h_mm: float):
    c.saveState()
    c.setLineWidth(BORDER_LINE_WIDTH_PT)
    x = BORDER_INSET_MM
    y = BORDER_INSET_MM
    w = label_w_mm - 2 * BORDER_INSET_MM
    h = label_h_mm - 2 * BORDER_INSET_MM
    c.roundRect(x * mm, y * mm, w * mm, h * mm, BORDER_RADIUS_MM * mm, stroke=1, fill=0)
    c.restoreState()

def draw_qr_svg(canvas_obj, data: str, x_mm: float, y_mm: float, size_mm: float, error_level: str = "Q", border_modules: int = 4):
    qr = segno.make(data, error=error_level)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", border=border_modules)
    buf.seek(0)

    drawing = svg2rlg(buf)
    target_pts = size_mm * mm
    scale = target_pts / max(drawing.width, drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)

    renderPDF.draw(drawing, canvas_obj, x_mm * mm, y_mm * mm)

def main():
    df = pd.read_csv(DF_PATH, dtype={"qr_data": "string"})
    c = canvas.Canvas(PDF_OUT, pagesize=(LABEL_W_MM * mm, LABEL_H_MM * mm))

    for _, row in df.iterrows():
        payload = str(row["qr_data"])
        
        # 1. Extract digits 10-14 (ignoring spaces)
        # e.g., "01 10 000 0100001 00 50" -> Index 9 to 14 is "00001"
        stripped_payload = payload.replace(" ", "")
        tote_id = stripped_payload[9:14]
        display_text = f"TOTE # {tote_id}"

        # 2. Draw the QR code
        draw_qr_svg(
            canvas_obj=c,
            data=payload,
            x_mm=QR_X_MM,
            y_mm=QR_Y_MM,
            size_mm=QR_SIZE_MM
        )

        # 3. Add Rotated Human Readable Text
        c.saveState()
        # Move the origin to where we want the text centered
        c.translate(TEXT_X_MM * mm, QR_CENTER_Y_MM * mm)
        c.rotate(90)  # Rotate CCW 90 degrees
        c.setFont("Helvetica-Bold", 11)
        # Draw centered at the new (0,0) origin
        c.drawCentredString(0, 0, display_text)
        c.restoreState()

        # 4. Draw Border
        draw_label_border(c, LABEL_W_MM, LABEL_H_MM)

        c.showPage()

    c.save()
    print(f"Wrote {PDF_OUT}")

if __name__ == "__main__":
    main()