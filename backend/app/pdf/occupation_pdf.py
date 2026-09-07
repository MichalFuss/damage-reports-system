"""
Re-occupation certificate PDF ("תיק אכלוס מחדש").

Hebrew, right-to-left, formally laid out. Rendering uses fpdf2 with HarfBuzz
text shaping so the bidi / RTL result is correct.

To mimic a heavier document pipeline the build sleeps for one second before
writing the file (as required by the Workshop 3 brief).
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

from ..domain import RESTORATION_COMPLETED

_FONT_DIR = Path(__file__).parent / "assets"
_FONT_REGULAR = _FONT_DIR / "NotoSansHebrew-Regular.ttf"

_NAVY = (0, 34, 68)
_BLUE = (0, 90, 156)
_GREY = (90, 106, 122)
_GREEN = (26, 122, 60)
_GREEN_BG = (230, 244, 236)
_LINE = (220, 232, 245)

_PAGE_W = 210.0
_MARGIN = 20.0
_INNER = _PAGE_W - 2 * _MARGIN


class _Doc(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(_MARGIN, 18, _MARGIN)
        self.set_auto_page_break(True, margin=18)
        self.add_font("noto", "", str(_FONT_REGULAR))
        self.add_font("noto", "B", str(_FONT_REGULAR))  # synthetic bold via style
        self.set_text_shaping(True, direction="rtl")

    def he(self, text: str, size: int, *, bold: bool = False, color=_NAVY,
           align: Align = Align.R, gap: float = 6.0) -> None:
        self.set_font("noto", "B" if bold else "", size)
        self.set_text_color(*color)
        self.multi_cell(_INNER, size * 0.55, text, align=align,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if gap:
            self.ln(gap)

    def rule(self, color=_LINE) -> None:
        self.set_draw_color(*color)
        self.set_line_width(0.4)
        y = self.get_y()
        self.line(_MARGIN, y, _PAGE_W - _MARGIN, y)
        self.ln(4)

    def field(self, label: str, value: str) -> None:
        self.set_font("noto", "B", 9)
        self.set_text_color(*_GREY)
        self.multi_cell(_INNER, 5, label, align=Align.R,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("noto", "", 12)
        self.set_text_color(30, 30, 30)
        self.multi_cell(_INNER, 6, value or "—", align=Align.R,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)


def _eligibility_label(building: dict) -> str:
    return "בדיקת זכאות בוצעה" if building.get("eligibilityChecked") else "בדיקת זכאות לא בוצעה"


def _budget_label(building: dict) -> str:
    return "קיימת בקשת תקציב" if building.get("budgetRequested") else "אין בקשת תקציב"


def _restoration_label(building: dict) -> str:
    return (
        "תהליך שיקום הסתיים"
        if building.get("status") == RESTORATION_COMPLETED
        else "תהליך שיקום לא הסתיים"
    )


def build_occupation_pdf(building: dict, output_dir: Path | str) -> str:
    """Render the certificate and return the generated file name."""
    time.sleep(1)  # simulate a heavier PDF pipeline (per the brief)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"reoccupation-{building['id']}-{uuid.uuid4().hex[:8]}.pdf"
    file_path = output_dir / file_name

    doc = _Doc()
    doc.add_page()

    # Header band
    doc.set_fill_color(*_NAVY)
    doc.rect(_MARGIN, doc.get_y(), _INNER, 16, style="F")
    doc.set_xy(_MARGIN, doc.get_y() + 3.5)
    doc.set_font("noto", "B", 15)
    doc.set_text_color(255, 255, 255)
    doc.multi_cell(_INNER, 8, "מדינת ישראל — משרד הבינוי והשיכון", align=Align.R,
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(10)

    doc.he("אישור חזרה לדירה", 24, bold=True, color=_NAVY, align=Align.C, gap=2)
    doc.he("תיק אכלוס מחדש", 13, color=_BLUE, align=Align.C, gap=6)
    doc.rule(_BLUE)

    doc.he("פרטי המבנה", 14, bold=True, gap=3)
    doc.field("מזהה מבנה", str(building.get("id", "")))
    doc.field("כתובת", str(building.get("address", "")))
    doc.field("מספר דירות", str(building.get("apartmentCount", 0)))
    doc.ln(2)

    doc.he("מצב המבנה", 14, bold=True, gap=3)
    doc.field("סטטוס זכאות", _eligibility_label(building))
    doc.field("סטטוס תקציב", _budget_label(building))
    doc.field("סטטוס שיקום", _restoration_label(building))
    doc.ln(4)

    # Green declaration banner
    banner_y = doc.get_y()
    doc.set_fill_color(*_GREEN_BG)
    doc.set_draw_color(*_GREEN)
    doc.rect(_MARGIN, banner_y, _INNER, 18, style="DF")
    doc.set_xy(_MARGIN, banner_y + 4.5)
    doc.set_font("noto", "B", 18)
    doc.set_text_color(*_GREEN)
    doc.multi_cell(_INNER, 9, "ניתן לאכלוס מחדש", align=Align.C,
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.set_y(banner_y + 24)

    doc.he(
        "המבנה עומד בתנאים הנדרשים לצורך חזרת דיירים לביתם.",
        11, color=_GREY, gap=8,
    )

    generated = datetime.now().strftime("%d/%m/%Y %H:%M")
    doc.he(f"תאריך הפקה: {generated}", 10, color=_GREY, gap=2)
    doc.he(
        "מסמך זה הופק אוטומטית על ידי מערכת ניהול דיווחי הנזק הלאומית.",
        8, color=_GREY, gap=0,
    )

    doc.output(str(file_path))
    return file_name
