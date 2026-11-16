#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic Admission Studio - Report Exporter
Generates comprehensive Excel and CSV summary sheets for faculty review.
"""

import os
import sys
import json
from datetime import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOLS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EXPORTS_DIR = os.path.join(PROJECT_ROOT, "exports")
DATA_FILE = os.path.join(DATA_DIR, "candidates_data.json")
EVAL_FILE = os.path.join(DATA_DIR, "candidate_evaluations.json")
SEATS_FILE = os.path.join(DATA_DIR, "seats_allocation.json")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")

def load_all_data():
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    candidates = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            candidates = json.load(f)

    evals = {}
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, "r", encoding="utf-8") as f:
                evals = json.load(f)
        except Exception:
            pass

    seats = {}
    if os.path.exists(SEATS_FILE):
        try:
            with open(SEATS_FILE, "r", encoding="utf-8") as f:
                seats = json.load(f)
        except Exception:
            pass

    for c in candidates:
        cid_str = str(c["id"])
        if cid_str in evals:
            for k, v in evals[cid_str].items():
                c[k] = v

    return config, candidates, seats

def export_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("❌ Error: openpyxl is not installed. Please run: pip install openpyxl")
        return

    config, candidates, seats = load_all_data()
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    # Reverse seat mapping: candidate_id -> seat info
    cand_seats = {}
    seats_config = config.get("seats", [])
    seats_map = {s["id"]: s for s in seats_config}
    for seat_id, cid in seats.items():
        if cid is not None:
            cand_seats[cid] = seats_map.get(seat_id, {"title": seat_id})

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "متقاضیان تحصیلات تکمیلی"
    ws.views.sheetView[0].rightToLeft = True

    font_title = Font(name="Tahoma", size=13, bold=True, color="1B365D")
    font_sub = Font(name="Tahoma", size=9.5, italic=True, color="555555")
    font_header = Font(name="Tahoma", size=10.5, bold=True, color="FFFFFF")
    font_data = Font(name="Tahoma", size=9.5)

    fill_header = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    border_cell = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    headers = [
        "ردیف", "نام و نام خانوادگی", "گرایش", "نوع قبولی / سهمیه", "رتبه کنکور / سهمیه",
        "معدل کارشناسی", "دانشگاه کارشناسی", "وضعیت بررسی", "نوبت مصاحبه", "تخصیص ظرفیت",
        "امتیاز ارزیابی", "یادداشت و جمع‌بندی استاد"
    ]

    lab_name = config.get("lab_name", "آزمایشگاه")
    year = config.get("academic_year", "")
    title = f"گزارش جامع متقاضیان و ارزیابی پذیرش {year} - {lab_name}"

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    c_title = ws.cell(row=1, column=1, value=title)
    c_title.font = font_title
    c_title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    ws.row_dimensions[3].height = 26
    for idx, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal="center", vertical="center")

    for r_idx, c in enumerate(candidates, 4):
        ws.row_dimensions[r_idx].height = 22
        assigned_seat = cand_seats.get(c["id"])
        seat_str = assigned_seat["title"] if assigned_seat else "-"

        row_vals = [
            r_idx - 3,
            c.get("name", "-"),
            c.get("track", "-"),
            c.get("quota", "-"),
            c.get("konkur_arshad", "-"),
            c.get("bsc_gpa", "-"),
            c.get("bsc_uni", "-"),
            c.get("status", "بررسی اولیه"),
            c.get("interview_slot") or "-",
            seat_str,
            c.get("score") if c.get("score") is not None else "-",
            c.get("eval_notes") or "-"
        ]

        is_even = (r_idx % 2 == 0)
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_data
            cell.border = border_cell
            if is_even:
                cell.fill = fill_zebra
            cell.alignment = Alignment(horizontal="center" if c_idx in [1, 3, 5, 6, 8, 9, 10, 11] else "right", vertical="center")

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(EXPORTS_DIR, f"admission_report_{timestamp}.xlsx")
    wb.save(out_file)
    print(f"✅ Exported Excel report to: {out_file}")

if __name__ == "__main__":
    export_excel()
