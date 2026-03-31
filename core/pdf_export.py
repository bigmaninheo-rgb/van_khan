from __future__ import annotations

from pathlib import Path

from fpdf import FPDF


def export_prayer_to_pdf(content: str, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    win_font = Path("C:/Windows/Fonts/arial.ttf")
    if win_font.exists():
        pdf.add_font("ArialUnicode", "", str(win_font))
        pdf.set_font("ArialUnicode", size=14)
    else:
        pdf.set_font("Helvetica", size=14)

    text_width = 190
    for line in content.splitlines():
        if line.strip():
            pdf.multi_cell(text_width, 8, line)
        else:
            pdf.ln(4)

    pdf.output(str(output))
    return output
