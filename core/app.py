#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic Admission Studio - Application Backend
Universal Web Server & REST API for Graduate Admission Dashboard
"""

import os
import json
from flask import Flask, render_template, jsonify, request, send_file, abort

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CORE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESUMES_DIR = os.path.join(PROJECT_ROOT, "resumes")
TEMPLATES_DIR = os.path.join(CORE_DIR, "templates")
STATIC_DIR = os.path.join(CORE_DIR, "static")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def load_config():
    default_config = {
        "institution": "دانشگاه علم و صنعت ایران",
        "department": "دانشکده مهندسی کامپیوتر",
        "lab_name": "آزمایشگاه داده‌کاوی",
        "lab_short": "DML",
        "supervisor_name": "دکتر بهروز مینایی بیدگلی",
        "academic_year": "۱۴۰۵ - ۱۴۰۶",
        "port": 5050,
        "interview_location_default": "تهران، رسالت، خیابان هنگام، دانشگاه علم و صنعت ایران، دانشکده مهندسی کامپیوتر، طبقه سوم، اتاق دکتر بهروز مینایی بیدگلی / آزمایشگاه داده‌کاوی (DML)",
        "interview_map_url": "https://nshn.ir/",
        "tracks": [],
        "seats": [],
        "email_templates": {}
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                default_config.update(json.load(f))
        except Exception as e:
            print("Warning loading config.json:", e)
    return default_config

config = load_config()

@app.after_request
def add_security_and_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

DATA_FILE = os.path.join(DATA_DIR, "candidates_data.json")
EVAL_FILE = os.path.join(DATA_DIR, "candidate_evaluations.json")
SEATS_FILE = os.path.join(DATA_DIR, "seats_allocation.json")

def load_candidates():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    # Merge with saved evaluations if any
    evals = {}
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, "r", encoding="utf-8") as ef:
                evals = json.load(ef)
        except Exception:
            evals = {}
            
    for c in candidates:
        cid_str = str(c["id"])
        if cid_str in evals:
            for k, v in evals[cid_str].items():
                c[k] = v

    def is_ai(c):
        return c.get('track_en') == 'AI' or 'هوش' in c.get('track', '')

    candidates.sort(key=lambda c: (
        0 if is_ai(c) else 1,
        0 if ('استعداد' in str(c.get('admission_type', '')) or 'استعداد' in str(c.get('quota', ''))) else 1,
        c.get('rank_val') if c.get('rank_val') is not None else 9999,
        -float(c.get('gpa_val', 0) or 0),
        c.get('id', 0)
    ))

    return candidates

def load_seats():
    default_seats = {}
    if config.get("seats"):
        for s in config["seats"]:
            default_seats[s["id"]] = None
    else:
        default_seats = {
            "ai_roz_1": None, "ai_roz_2": None, "ai_shab_1": None, "ai_shab_2": None,
            "sw_roz_1": None, "sw_roz_2": None, "sw_roz_3": None, "sw_roz_4": None
        }

    if not os.path.exists(SEATS_FILE):
        return default_seats
    try:
        with open(SEATS_FILE, "r", encoding="utf-8") as sf:
            seats = json.load(sf)
            for k in default_seats:
                if k in seats:
                    default_seats[k] = seats[k]
            return default_seats
    except Exception:
        return default_seats

def save_seats(seats_data):
    with open(SEATS_FILE, "w", encoding="utf-8") as sf:
        json.dump(seats_data, sf, ensure_ascii=False, indent=2)

def save_evaluation(cid, eval_data):
    evals = {}
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, "r", encoding="utf-8") as ef:
                evals = json.load(ef)
        except Exception:
            evals = {}
            
    evals[str(cid)] = eval_data
    with open(EVAL_FILE, "w", encoding="utf-8") as ef:
        json.dump(evals, ef, ensure_ascii=False, indent=2)

    # Sync to candidates_data.json
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as df:
                cands = json.load(df)
            for c in cands:
                if c["id"] == cid:
                    for k, v in eval_data.items():
                        c[k] = v
                    break
            with open(DATA_FILE, "w", encoding="utf-8") as df:
                json.dump(cands, df, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Warning syncing candidates_data.json:", e)

@app.route("/")
def index():
    candidates = load_candidates()
    seats = load_seats()
    return render_template("index.html", candidates=candidates, seats=seats)

@app.route("/api/config")
def api_get_config():
    return jsonify(load_config())

@app.route("/api/candidates")
def api_candidates():
    return jsonify(load_candidates())

@app.route("/api/candidate/<int:cid>/eval", methods=["POST"])
def api_save_eval(cid):
    data = request.json or {}
    allowed_keys = ["status", "score", "interview_slot", "interview_type", "eval_notes", "interview_phase"]
    evals = {}
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, "r", encoding="utf-8") as ef:
                evals = json.load(ef)
        except Exception:
            evals = {}
    existing_c_eval = evals.get(str(cid), {})
    for k in allowed_keys:
        if k in data:
            existing_c_eval[k] = data[k]
    save_evaluation(cid, existing_c_eval)
    return jsonify({"success": True, "cid": cid, "data": existing_c_eval})

@app.route("/api/seats", methods=["GET", "POST"])
def api_seats():
    if request.method == "POST":
        data = request.json or {}
        current_seats = load_seats()
        current_seats.update(data)
        save_seats(current_seats)
        return jsonify({"success": True, "seats": current_seats})
    return jsonify(load_seats())

@app.route("/api/seats/reset", methods=["POST"])
def api_reset_seats():
    empty_seats = {k: None for k in load_seats().keys()}
    save_seats(empty_seats)
    return jsonify({"success": True, "seats": empty_seats})

@app.route("/api/export/excel", methods=["POST"])
def api_export_excel():
    import io
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    payload = request.json or {}
    headers = payload.get("headers", [])
    rows = payload.get("rows", [])
    current_cfg = load_config()
    default_title = f"فهرست متقاضیان {current_cfg.get('lab_name', 'آزمایشگاه')}"
    title = payload.get("title", default_title)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "متقاضیان"
    ws.views.sheetView[0].rightToLeft = True

    font_title = Font(name="Tahoma", size=13, bold=True, color="1B365D")
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

    num_cols = max(len(headers), 1)

    # Title row
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
    cell_title = ws.cell(row=1, column=1, value=title)
    cell_title.font = font_title
    cell_title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    # Header row
    ws.row_dimensions[3].height = 26
    for col_idx, h_text in enumerate(headers, 1):
        c = ws.cell(row=3, column=col_idx, value=h_text)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Data rows
    for r_idx, r_data in enumerate(rows, 4):
        ws.row_dimensions[r_idx].height = 20
        is_even = (r_idx % 2 == 0)
        for c_idx, val in enumerate(r_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_data
            cell.border = border_cell
            if is_even:
                cell.fill = fill_zebra
            cell.alignment = Alignment(horizontal="center" if c_idx in [1, 2, 4, 5, 8] else "right", vertical="center")

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = "applicants_report.xlsx"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def resolve_file_path(filename):
    clean = filename.lstrip("/")
    if clean.startswith("resumes/"):
        clean = clean[len("resumes/"):]
    p = os.path.join(RESUMES_DIR, clean)
    if os.path.exists(p):
        return p
    p = os.path.join(PROJECT_ROOT, clean)
    if os.path.exists(p):
        return p
    p = os.path.join(CORE_DIR, clean)
    if os.path.exists(p):
        return p
    return None

@app.route("/files/<path:filename>")
def serve_file(filename):
    file_path = resolve_file_path(filename)
    if not file_path:
        abort(404)
    if filename.lower().endswith(".pdf"):
        return send_file(file_path, mimetype="application/pdf", as_attachment=False)
    elif filename.lower().endswith(".txt"):
        return send_file(file_path, mimetype="text/plain; charset=utf-8", as_attachment=False)
    return send_file(file_path, as_attachment=False)

@app.route("/download/<path:filename>")
def download_file(filename):
    file_path = resolve_file_path(filename)
    if not file_path:
        abort(404)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    current_cfg = load_config()
    port = int(os.environ.get("PORT", current_cfg.get("port", 5050)))
    print(f"============================================================")
    print(f"  {current_cfg.get('lab_name', 'Academic Studio')} Running at:")
    print(f"  >>> http://127.0.0.1:{port} <<<")
    print(f"============================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
