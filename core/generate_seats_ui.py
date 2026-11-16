import json
import os

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CORE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_FILE = os.path.join(DATA_DIR, "candidates_data.json")
EVAL_FILE = os.path.join(DATA_DIR, "candidate_evaluations.json")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")

config = {
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
        with open(CONFIG_FILE, "r", encoding="utf-8") as cf:
            config.update(json.load(cf))
    except Exception as e:
        print("Warning loading config.json:", e)

# Fallback if running directly in data dir
if not os.path.exists(DATA_FILE) and os.path.exists("candidates_data.json"):
    DATA_FILE = "candidates_data.json"
    EVAL_FILE = "candidate_evaluations.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    candidates = json.load(f)

# Always merge with candidate_evaluations.json if present
if os.path.exists(EVAL_FILE):
    try:
        with open(EVAL_FILE, "r", encoding="utf-8") as ef:
            evals = json.load(ef)
        for c in candidates:
            cid_str = str(c["id"])
            if cid_str in evals:
                for k, v in evals[cid_str].items():
                    c[k] = v
    except Exception as e:
        print("Warning loading evaluations in generate_seats_ui:", e)

# Sort candidates by default track order (AI first, then Software, sorted by merit)
def is_ai(c):
    return c.get('track_en') == 'AI' or 'هوش' in c.get('track', '')

candidates.sort(key=lambda c: (
    0 if is_ai(c) else 1,
    0 if ('استعداد' in str(c.get('admission_type', '')) or 'استعداد' in str(c.get('quota', ''))) else 1,
    c.get('rank_val') if c.get('rank_val') is not None else 9999,
    -float(c.get('gpa_val', 0) or 0),
    c.get('id', 0)
))

def get_candidates_json(is_standalone=False):
    import copy
    cands = copy.deepcopy(candidates)
    if is_standalone:
        for c in cands:
            pdf_path = c['primary_pdf'].replace('/files/', '')
            if not pdf_path.startswith('resumes/'):
                pdf_path = 'resumes/' + pdf_path
            c['primary_pdf'] = pdf_path
            for fl in c['files']:
                fl_path = fl['rel_url'].replace('/files/', '')
                if not fl_path.startswith('resumes/'):
                    fl_path = 'resumes/' + fl_path
                fl['rel_url'] = fl_path
    return json.dumps(cands, ensure_ascii=False)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <title>پذیرش متقاضیان تحصیلات تکمیلی __ACADEMIC_YEAR__ | __LAB_NAME__ (__LAB_SHORT__)</title>
  
  <!-- Fonts: Vazirmatn -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --color-paper: #FAF7EE;
      --color-paper-card: #FFFFFF;
      --color-paper-alt: #F3EFE3;
      --color-ink: #1A1915;
      --color-ink-muted: #6B685C;
      --color-border: #1A1915;
      --color-ai: #0E7C86;
      --color-ai-light: #E6F5F6;
      --color-sw: #C0392B;
      --color-sw-light: #FDEEEB;
      --color-shabaneh: #4A235A;
      --color-shabaneh-light: #F4ECF7;
      --color-gold: #B8860B;
      --color-gold-light: #FFF9E6;
      --color-stamp: #E0503F;
      --color-gray: #A8A291;
      --color-success: #15803D;
      --color-success-light: #DCFCE7;
      --shadow-retro: 3px 3px 0px var(--color-ink);
      --shadow-card: 4px 4px 0px var(--color-ink);
      --shadow-card-hover: 7px 7px 0px var(--color-ink);
      --font-main: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, sans-serif;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, Arial, sans-serif !important;
    }

    body, button, input, select, textarea, optgroup, option, table, th, td, h1, h2, h3, h4, h5, h6, span, div, p, a, b, strong, em, label {
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, Arial, sans-serif !important;
    }

    body {
      font-family: var(--font-main);
      background-color: var(--color-paper);
      color: var(--color-ink);
      line-height: 1.6;
      direction: rtl;
      text-align: right;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
      padding-bottom: 70px;
    }

    /* Vintage Paper Texture Overlay */
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      background-image: radial-gradient(rgba(26,25,21,0.035) 1px, transparent 1px);
      background-size: 24px 24px;
      pointer-events: none;
      z-index: 9999;
    }

    /* Top Header */
    .top-header {
      background: var(--color-ink);
      color: var(--color-paper);
      border-bottom: 3px solid var(--color-stamp);
      padding: 12px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    .brand-block {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-badge {
      background: var(--color-paper);
      color: var(--color-ink);
      font-weight: 900;
      font-size: 20px;
      padding: 6px 14px;
      border: 2px solid var(--color-paper);
      letter-spacing: 1px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .brand-title h1 {
      font-size: 20px;
      font-weight: 800;
      margin: 0;
      color: var(--color-paper);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-title p {
      font-size: 13px;
      color: var(--color-gray);
      margin: 2px 0 0;
    }

    .header-center {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .live-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(224, 80, 63, 0.2);
      border: 1px solid var(--color-stamp);
      padding: 4px 12px;
      border-radius: 2px;
      font-size: 13px;
      font-weight: 700;
      color: #FF7675;
    }

    .pulse-dot {
      width: 10px;
      height: 10px;
      background-color: var(--color-stamp);
      border-radius: 50%;
      animation: pulse 1.4s infinite ease-in-out;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(0.9); opacity: 0.8; }
      50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 10px var(--color-stamp); }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn-header {
      background: transparent;
      color: var(--color-paper);
      border: 1.5px solid var(--color-gray);
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      text-decoration: none;
      font-family: inherit;
    }

    .btn-header:hover {
      background: var(--color-paper);
      color: var(--color-ink);
      border-color: var(--color-paper);
    }

    .btn-header.primary {
      background: var(--color-stamp);
      color: var(--color-paper);
      border-color: var(--color-stamp);
    }

    .btn-header.primary:hover {
      background: #c0392b;
    }

    /* Ticker Band */
    .ticker-band {
      background: var(--color-paper-alt);
      border-bottom: 2px solid var(--color-ink);
      padding: 8px 32px;
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 14px;
      font-weight: 700;
      overflow: hidden;
    }

    .ticker-tag {
      background: var(--color-stamp);
      color: var(--color-paper);
      font-size: 11px;
      font-weight: 900;
      padding: 3px 8px;
      letter-spacing: 0.5px;
      border-radius: 2px;
      flex-shrink: 0;
    }

    .ticker-content {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--color-ink);
      flex: 1;
    }

    /* Navigation Bar */
    .nav-tabs-bar {
      background: var(--color-paper);
      border-bottom: 2px solid var(--color-ink);
      padding: 0 32px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      white-space: nowrap;
    }

    .nav-tab-btn {
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      color: var(--color-ink-muted);
      font-family: inherit;
      font-size: 15px;
      font-weight: 700;
      padding: 14px 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      margin-bottom: -2px;
    }

    .nav-tab-btn:hover {
      color: var(--color-ink);
      background: rgba(26,25,21,0.03);
    }

    .nav-tab-btn.active {
      color: var(--color-ink);
      border-bottom-color: var(--color-stamp);
      background: var(--color-paper-card);
      border-top: 2px solid var(--color-ink);
      border-right: 2px solid var(--color-ink);
      border-left: 2px solid var(--color-ink);
    }

    .tab-badge {
      background: var(--color-ink);
      color: var(--color-paper);
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 10px;
      font-weight: 800;
    }

    /* Main Container */
    .main-container {
      max-width: 100%;
      width: 100%;
      margin: 0 auto;
      padding: 12px 16px 60px;
    }

    .view-section {
      display: none;
    }

    .view-section.active {
      display: block;
    }

    /* ========================================================
       COMPACT LAB CAPACITY & SEATS
       ======================================================== */
    .capacity-compact-box {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: 4px 4px 0px var(--color-ink);
      padding: 10px 14px;
      margin-bottom: 14px;
      border-radius: 4px;
    }

    .compact-cap-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 8px;
      padding-bottom: 6px;
      border-bottom: 1.5px solid var(--color-paper-alt);
    }

    .cap-pill {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 10px;
      border: 1px solid var(--color-ink);
      background: var(--color-paper);
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }

    .cap-pill.sw { background: #FEF2F2; color: var(--color-sw); border-color: #FECACA; }
    .cap-pill.ai { background: #F0FDFA; color: var(--color-ai); border-color: #99F6E4; }
    .cap-pill.shab { background: #FAF5FF; color: var(--color-shabaneh); border-color: #E9D5FF; }

    .seats-matrix-wrapper {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 8px;
    }

    .seats-row-block {
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 9px 12px 11px;
    }

    .seats-row-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      padding-bottom: 5px;
      border-bottom: 1px dashed #CBD5E1;
    }

    .seats-row-badge {
      font-size: 12px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .seats-row-badge.ai { color: var(--color-ai); }
    .seats-row-badge.sw { color: var(--color-sw); }

    .seats-row-sub {
      font-size: 10.5px;
      color: #64748B;
      font-weight: 600;
    }

    .seats-grid-ai {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }

    .seats-grid-sw {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }

    @media (max-width: 1024px) {
      .seats-grid-ai {
        grid-template-columns: repeat(2, 1fr);
      }
      .seats-grid-sw {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 680px) {
      .seats-grid-ai, .seats-grid-sw {
        grid-template-columns: 1fr;
      }
    }

    .compact-seat-card {
      background: #FFFFFF;
      border: 1.5px solid #CBD5E1;
      border-radius: 5px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 84px;
      transition: all 0.15s ease;
      box-sizing: border-box;
      position: relative;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    .compact-seat-card:hover {
      border-color: #94A3B8;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    .compact-seat-card.sw_roz { border-top: 3.5px solid var(--color-sw); }
    .compact-seat-card.ai_roz { border-top: 3.5px solid var(--color-ai); }
    .compact-seat-card.ai_shab { border-top: 3.5px solid var(--color-shabaneh); }

    .compact-seat-card.occupied {
      background: #FFFFFF;
      border-color: var(--color-ink);
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    .compact-seat-card.occupied.sw { border-top: 4px solid var(--color-sw); }
    .compact-seat-card.occupied.ai { border-top: 4px solid var(--color-ai); }
    .compact-seat-card.occupied.shab { border-top: 4px solid var(--color-shabaneh); }
    .compact-seat-card.occupied.talented { border-top: 4px solid var(--color-gold); }

    .compact-seat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11.5px;
      font-weight: 800;
      color: var(--color-ink);
      line-height: 1.2;
      margin-bottom: 4px;
    }

    .compact-seat-tag {
      font-size: 10px;
      font-weight: 700;
      color: #64748B;
      background: #F1F5F9;
      padding: 2px 6px;
      border-radius: 3px;
      border: 1px solid #E2E8F0;
    }

    .compact-seat-vacate {
      background: #FEE2E2;
      border: 1px solid #FECACA;
      color: var(--color-stamp);
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      padding: 2px 6px;
      border-radius: 3px;
      line-height: 1;
      display: inline-flex;
      align-items: center;
      gap: 2px;
      transition: all 0.15s ease;
    }

    .compact-seat-vacate:hover {
      background: var(--color-stamp);
      color: #FFFFFF;
    }

    .compact-seat-body.occupied {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      margin-top: 2px;
    }

    .compact-seat-avatar {
      width: 28px;
      height: 28px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 11px;
      font-weight: 900;
      flex-shrink: 0;
      border: 1.5px solid var(--color-ink);
    }

    .compact-seat-info {
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: center;
      line-height: 1.3;
      flex: 1;
      min-width: 0;
    }

    .compact-seat-name {
      font-size: 12px;
      font-weight: 800;
      color: var(--color-ink);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .compact-seat-meta {
      font-size: 10px;
      color: var(--color-ink-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      display: flex;
      gap: 4px;
      align-items: center;
    }

    .btn-seat-choose {
      width: 100%;
      height: 32px;
      margin-top: 2px;
      background: #FFFFFF;
      border: 1.5px dashed #0284C7;
      border-radius: 4px;
      color: #0284C7;
      font-size: 11px;
      font-weight: 800;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      transition: all 0.15s ease;
      padding: 0 8px;
      box-sizing: border-box;
      direction: rtl;
    }

    .btn-seat-choose:hover {
      background: #0284C7;
      color: #FFFFFF;
      border-style: solid;
      border-color: #0284C7;
      box-shadow: 0 2px 5px rgba(2, 132, 199, 0.25);
      transform: translateY(-1px);
    }

    .btn-seat-count-tag {
      font-size: 9.5px;
      font-weight: 800;
      padding: 1.5px 6px;
      border-radius: 3px;
      background: #E0F2FE;
      color: #0369A1;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .btn-seat-choose:hover .btn-seat-count-tag {
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
    }

    /* Controls Bar */
    .controls-bar {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      padding: 16px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .filters-group {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }

    .filter-btn {
      background: var(--color-paper);
      border: 1.5px solid var(--color-ink);
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
      box-shadow: 1.5px 1.5px 0px var(--color-ink);
    }

    .filter-btn:hover {
      transform: translate(-1px, -1px);
      box-shadow: 2.5px 2.5px 0px var(--color-ink);
    }

    .filter-btn.active {
      background: var(--color-ink);
      color: var(--color-paper);
    }

    .filter-btn.accepted-filter.active {
      background: var(--color-success);
      color: #FFF;
    }

    .search-sort-group {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .search-box {
      position: relative;
    }

    .search-input {
      background: var(--color-paper);
      border: 1.5px solid var(--color-ink);
      padding: 8px 36px 8px 12px;
      font-size: 13px;
      font-family: inherit;
      width: 240px;
      transition: width 0.2s ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--color-stamp);
      width: 280px;
      background: #FFF;
    }

    .search-icon {
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      pointer-events: none;
      color: var(--color-ink-muted);
    }

    .select-sort {
      background: var(--color-paper);
      border: 1.5px solid var(--color-ink);
      padding: 8px 12px;
      font-size: 13px;
      font-family: inherit;
      font-weight: 600;
      cursor: pointer;
    }

    .view-toggle-btns {
      display: flex;
      border: 1.5px solid var(--color-ink);
    }

    .view-toggle-btn {
      background: var(--color-paper);
      border: none;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .view-toggle-btn.active {
      background: var(--color-ink);
      color: var(--color-paper);
    }

    /* Candidate Cards */
    .candidates-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }

    .candidate-card {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      display: flex;
      flex-direction: column;
      transition: all 0.2s ease;
      position: relative;
    }

    .candidate-card:hover {
      transform: translate(-3px, -3px);
      box-shadow: var(--shadow-card-hover);
    }

    .candidate-card.is-accepted {
      border: 3px solid var(--color-success);
      box-shadow: 4px 4px 0px var(--color-success);
    }

    .candidate-card.is-rejected {
      opacity: 0.78;
      background: #FFFDFD;
      border-color: #F87171;
      box-shadow: 2px 2px 0px rgba(220, 38, 38, 0.25);
    }

    .candidate-card.is-rejected:hover {
      opacity: 0.95;
      border-color: #DC2626;
      box-shadow: 3px 3px 0px rgba(220, 38, 38, 0.35);
    }

    .name-strikethrough {
      text-decoration: line-through !important;
      text-decoration-color: #DC2626 !important;
      text-decoration-thickness: 2.5px !important;
      color: #64748B !important;
    }

    tr.row-rejected {
      background-color: #FFF5F5 !important;
      opacity: 0.82;
    }

    tr.row-rejected:hover {
      background-color: #FEE2E2 !important;
      opacity: 1;
    }

    tr.row-rejected td {
      color: #64748B;
    }

    .card-top {
      padding: 16px;
      border-bottom: 1.5px solid var(--color-paper-alt);
      display: flex;
      align-items: flex-start;
      gap: 12px;
      position: relative;
    }

    .card-monogram {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFF;
      font-size: 18px;
      font-weight: 900;
      border: 2px solid var(--color-ink);
      box-shadow: 2px 2px 0px var(--color-ink);
      flex-shrink: 0;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .card-monogram:hover {
      transform: translate(-1px, -1px);
      box-shadow: 3px 3px 0px var(--color-ink);
    }

    .card-title-meta {
      flex: 1;
      min-width: 0;
    }

    .card-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .card-name-wrapper {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      cursor: pointer;
      padding: 3px 6px;
      margin: -3px -6px;
      border-radius: 6px;
      transition: all 0.15s ease;
      min-width: 0;
      flex: 1;
      text-decoration: none;
    }

    .card-name-wrapper:hover {
      background: #F0F9FF;
    }

    .card-name-wrapper:hover .card-name {
      color: #0284C7;
      text-decoration: underline;
      text-decoration-thickness: 1.5px;
    }

    .card-name-wrapper:hover .card-dossier-pill {
      background: #0284C7;
      color: #FFFFFF;
      border-color: #0284C7;
      box-shadow: 0 1px 3px rgba(2, 132, 199, 0.35);
    }

    .card-name {
      font-size: 16.5px;
      font-weight: 800;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--color-ink);
      transition: color 0.15s ease;
    }

    .card-dossier-pill {
      font-size: 11px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 4px;
      background: #F0F9FF;
      color: #0284C7;
      border: 1.5px solid #BAE6FD;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }

    .btn-star-card {
      background: none;
      border: none;
      font-size: 18px;
      cursor: pointer;
      color: #D1D5DB;
      transition: transform 0.15s ease, color 0.15s ease;
    }

    .btn-star-card.starred {
      color: #F59E0B;
      transform: scale(1.15);
    }

    .card-badges-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }

    .badge-pill {
      font-size: 11px;
      font-weight: 800;
      padding: 2px 8px;
      border: 1px solid var(--color-ink);
      border-radius: 2px;
      white-space: nowrap !important;
      display: inline-block !important;
    }

    .badge-pill.ai { background: var(--color-ai-light); color: var(--color-ai); }
    .badge-pill.sw { background: var(--color-sw-light); color: var(--color-sw); }
    .badge-pill.rank { background: #FEF3C7; color: #92400E; }
    .badge-pill.quota { background: #F3F4F6; color: #374151; }
    .badge-pill.accepted { background: var(--color-success-light); color: var(--color-success); border-color: var(--color-success); }
    .badge-pill.phase1, .badge-pill.phase-phase1 { background: #F3E8FF; color: #6D28D9; border-color: #8B5CF6; font-weight: 800; }
    .badge-pill.phase2, .badge-pill.phase-phase2 { background: #E0F2FE; color: #0369A1; border-color: #38BDF8; font-weight: 800; }
    .badge-pill.phase3, .badge-pill.phase-phase3 { background: #FEF3C7; color: #B45309; border-color: #F59E0B; font-weight: 800; }
    .badge-pill.phase-none { background: #F1F5F9; color: #64748B; border-color: #CBD5E1; }

    .phase-select {
      font-family: inherit;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 6px;
      border-radius: 4px;
      border: 1.5px solid #CBD5E1;
      background-color: #FFFFFF;
      cursor: pointer;
      transition: all 0.2s ease;
      outline: none;
    }
    .phase-select:focus {
      border-color: #7C3AED;
      box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
    }
    .phase-select.phase-phase1 {
      background-color: #F3E8FF;
      color: #6D28D9;
      border-color: #A78BFA;
    }
    .phase-select.phase-phase2 {
      background-color: #E0F2FE;
      color: #0369A1;
      border-color: #38BDF8;
    }
    .phase-select.phase-phase3 {
      background-color: #FEF3C7;
      color: #B45309;
      border-color: #F59E0B;
    }
    .phase-select.phase-none {
      background-color: #F8FAFC;
      color: #64748B;
      border-color: #CBD5E1;
    }

    .phase-tab-btn {
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 4px;
      border: 1.5px solid #CBD5E1;
      background: #FFFFFF;
      color: #334155;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .phase-tab-btn:hover {
      border-color: #94A3B8;
      background: #F8FAFC;
    }
    
    /* EXPORT STUDIO STYLES */
    .export-preset-btn {
      font-family: inherit;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 10px;
      border: 1.5px solid var(--color-ink);
      border-radius: 3px;
      background: #FFFFFF;
      color: var(--color-ink);
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }
    .export-preset-btn:hover {
      background: var(--color-ink);
      color: #FFFFFF;
      transform: translateY(-1px);
      box-shadow: 2px 2px 0px rgba(0,0,0,0.2);
    }
    .column-check-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 3px;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.12s ease;
      user-select: none;
    }
    .column-check-item:hover {
      background: #EFF6FF;
      border-color: #93C5FD;
    }
    .column-check-item.active {
      background: #F0FDF4;
      border-color: #86EFAC;
      font-weight: 800;
    }
    .column-check-item input[type="checkbox"] {
      cursor: pointer;
      accent-color: var(--color-success);
    }

    @media print {
      body * {
        visibility: hidden !important;
      }
      #printableReportArea, #printableReportArea * {
        visibility: visible !important;
      }
      #printableReportArea {
        display: block !important;
        position: absolute !important;
        left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 10mm 15mm !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: none !important;
      }
      .print-no-break {
        page-break-inside: avoid;
      }
    }

.phase-tab-btn.active {
      font-weight: 900;
      box-shadow: 2px 2px 0px var(--color-ink);
      transform: translate(-1px, -1px);
    }
    .phase-tab-btn.phase-1-btn.active {
      background: #7C3AED;
      color: #FFFFFF;
      border-color: #5B21B6;
    }
    .phase-tab-btn.phase-2-btn.active {
      background: #0284C7;
      color: #FFFFFF;
      border-color: #0369A1;
    }
    .phase-tab-btn.phase-3-btn.active {
      background: #D97706;
      color: #FFFFFF;
      border-color: #B45309;
    }
    .phase-tab-btn.phase-none-btn.active {
      background: #475569;
      color: #FFFFFF;
      border-color: #1E293B;
    }
    #btnPhaseAll.active {
      background: var(--color-ink);
      color: #FFFFFF;
      border-color: var(--color-ink);
    }

    .card-body {
      padding: 14px 16px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 9px;
      font-size: 13px;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }

    .card-body:hover {
      background-color: rgba(248, 250, 252, 0.75);
    }

    .card-body-click-prompt {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px dashed #CBD5E1;
      font-size: 11px;
      font-weight: 800;
      color: #0284C7;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.15s ease;
    }

    .candidate-card:hover .card-body-click-prompt {
      color: #0369A1;
    }

    .card-body-click-prompt .arrow-hint {
      font-size: 13px;
      transition: transform 0.15s ease;
    }

    .candidate-card:hover .card-body-click-prompt .arrow-hint {
      transform: translateX(-4px);
    }

    .card-info-row {
      display: flex;
      align-items: baseline;
      gap: 8px;
      color: var(--color-ink);
    }

    .info-label {
      color: var(--color-ink-muted);
      font-weight: 600;
      width: 85px;
      flex-shrink: 0;
      font-size: 12px;
    }

    .info-val {
      font-weight: 700;
      flex: 1;
    }

    .quick-copy-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      font-size: 11px;
      color: var(--color-ai);
      padding: 0 4px;
      font-weight: 700;
      text-decoration: underline;
    }

    .skills-tags-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 4px;
    }

    .skill-tag {
      background: var(--color-paper-alt);
      font-size: 11px;
      font-weight: 600;
      padding: 2px 6px;
      border: 1px solid rgba(26,25,21,0.2);
    }

    /* Card Footer & Accept Button */
    .card-footer {
      background: var(--color-paper-alt);
      border-top: 1.5px solid var(--color-ink);
      padding: 10px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .card-actions-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      flex-wrap: wrap;
    }

    .card-btn {
      background: var(--color-paper);
      border: 1.5px solid var(--color-ink);
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      display: flex;
      align-items: center;
      gap: 4px;
      box-shadow: 1.5px 1.5px 0px var(--color-ink);
      transition: all 0.15s ease;
      text-decoration: none;
      color: var(--color-ink);
    }

    .card-btn:hover {
      transform: translate(-1px, -1px);
      box-shadow: 2.5px 2.5px 0px var(--color-ink);
      background: #FFF;
    }

    /* BIG ACCEPT / REJECT BUTTON */
    .btn-accept-seat {
      width: 100%;
      background: #16A34A;
      color: #FFFFFF;
      border: 2px solid var(--color-ink);
      padding: 8px 12px;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
      font-family: inherit;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      box-shadow: 2px 2px 0px var(--color-ink);
      transition: all 0.15s ease;
    }

    .btn-accept-seat:hover {
      background: #15803D;
      transform: translate(-1px, -1px);
      box-shadow: 3px 3px 0px var(--color-ink);
    }

    .btn-accept-seat.is-assigned {
      background: var(--color-ink);
      color: #FEF08A;
      border-color: var(--color-ink);
    }

    .btn-accept-seat.is-assigned:hover {
      background: #DC2626;
      color: #FFF;
    }

    /* Table Container & Excel Table (Optimized for full visibility without horizontal scroll) */
    .table-container {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      overflow-x: auto;
      width: 100%;
      max-width: 100%;
      border-radius: 4px;
      margin-bottom: 24px;
    }

    .excel-table {
      width: 100%;
      max-width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      font-size: 11px;
      text-align: right;
    }

    .excel-table th {
      background: #213A79;
      color: #FFF;
      font-weight: 800;
      padding: 7px 3px;
      border: 1px solid #CCD6E0;
      font-size: 11px;
      line-height: 1.25;
      text-align: center;
      position: sticky;
      top: 0;
      z-index: 10;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: normal;
    }

    .excel-table td {
      padding: 5px 3px;
      border: 1px solid #E2E8F0;
      vertical-align: middle;
      font-size: 11px;
      line-height: 1.3;
      word-break: normal;
      overflow: hidden;
    }

    .excel-table .badge-pill {
      font-size: 9.5px !important;
      padding: 2px 4px !important;
      line-height: 1.25 !important;
      border-radius: 3px !important;
      display: inline-block !important;
      white-space: normal !important;
      text-align: center !important;
      max-width: 100% !important;
    }

    .excel-table .card-btn {
      font-size: 9.5px !important;
      padding: 2px 5px !important;
      line-height: 1.25 !important;
      border-radius: 3px !important;
    }

    .excel-table tr:nth-child(even) {
      background-color: #F8FAFC;
    }

    .excel-table tr:hover {
      background-color: #FEF3C7;
      cursor: pointer;
    }

    /* Modal Styles */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(26,25,21,0.65);
      backdrop-filter: blur(2px);
      z-index: 2000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal-overlay.active {
      display: flex;
    }

    .dossier-modal {
      background: var(--color-paper);
      border: 3px solid var(--color-ink);
      box-shadow: 10px 10px 0px var(--color-ink);
      width: 100%;
      max-width: 1100px;
      height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalSlide 0.2s ease-out;
    }

    @keyframes modalSlide {
      from { transform: translateY(20px) scale(0.98); opacity: 0; }
      to { transform: translateY(0) scale(1); opacity: 1; }
    }

    .modal-header {
      background: var(--color-ink);
      color: var(--color-paper);
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid var(--color-border);
    }

    .modal-candidate-profile {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .modal-monogram {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: 900;
      border: 2px solid var(--color-paper);
      color: #FFF;
    }

    .modal-title-box h2 {
      font-size: 20px;
      font-weight: 800;
      color: var(--color-paper);
      margin: 0;
    }

    .modal-title-box p {
      font-size: 13px;
      color: var(--color-gray);
      margin-top: 2px;
    }

    .modal-close-btn {
      background: transparent;
      border: 2px solid var(--color-gray);
      color: var(--color-paper);
      width: 36px;
      height: 36px;
      font-size: 20px;
      font-weight: 900;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: inherit;
    }

    .modal-close-btn:hover {
      background: var(--color-stamp);
      border-color: var(--color-stamp);
    }

    .modal-tabs-bar {
      background: var(--color-paper-alt);
      border-bottom: 2px solid var(--color-ink);
      padding: 0 24px;
      display: flex;
      gap: 8px;
    }

    .modal-tab-btn {
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      color: var(--color-ink-muted);
      font-family: inherit;
      font-size: 14px;
      font-weight: 700;
      padding: 12px 18px;
      cursor: pointer;
      margin-bottom: -2px;
    }

    .modal-tab-btn.active {
      color: var(--color-ink);
      border-bottom-color: var(--color-stamp);
      background: var(--color-paper);
      border-top: 2px solid var(--color-ink);
      border-right: 2px solid var(--color-ink);
      border-left: 2px solid var(--color-ink);
    }

    .modal-body {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      background: var(--color-paper);
    }

    .modal-tab-pane {
      display: none;
    }

    .modal-tab-pane.active {
      display: block;
    }

    .pdf-viewer-frame {
      width: 100%;
      height: 65vh;
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-retro);
      background: #525659;
    }

    .pdf-actions-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .pdf-selector-btns {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .email-container {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-retro);
      padding: 24px;
    }

    .email-header-meta {
      border-bottom: 2px solid var(--color-ink);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }

    .email-meta-line {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 6px;
      font-size: 13px;
    }

    .email-body-text {
      white-space: pre-wrap;
      line-height: 1.8;
      font-size: 14px;
      color: var(--color-ink);
    }

    .eval-form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    @media (max-width: 768px) {
      .eval-form-grid { grid-template-columns: 1fr; }
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-group label {
      font-weight: 700;
      font-size: 13px;
      color: var(--color-ink);
    }

    .form-control {
      background: var(--color-paper-card);
      border: 1.5px solid var(--color-ink);
      padding: 10px 12px;
      font-family: inherit;
      font-size: 14px;
      color: var(--color-ink);
    }

    .form-control:focus {
      outline: none;
      border-color: var(--color-stamp);
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    .page-footer {
      border-top: 2px solid var(--color-ink);
      background: var(--color-paper-alt);
      padding: 20px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      font-size: 13px;
      font-weight: 600;
      color: var(--color-ink-muted);
      margin-top: 40px;
    }

    .toast-msg {
      position: fixed;
      bottom: 24px;
      left: 24px;
      background: var(--color-ink);
      color: var(--color-paper);
      border: 2px solid var(--color-stamp);
      padding: 12px 20px;
      font-weight: 700;
      box-shadow: 4px 4px 0px rgba(0,0,0,0.3);
      z-index: 9999;
      display: none;
      align-items: center;
      gap: 10px;
    }

    /* ==========================================
       MODERN SHAMSI DATE & TIME PICKER MODAL
       ========================================== */
    .shamsi-modal-box {
      background: var(--color-paper);
      border: 2px solid var(--color-ink);
      box-shadow: 8px 8px 0px var(--color-ink);
      border-radius: 14px;
      width: 95%;
      max-width: 640px;
      max-height: 92vh;
      display: flex;
      flex-direction: column;
      position: relative;
      animation: modalSlide 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      overflow: hidden;
    }

    .shamsi-modal-header {
      background: linear-gradient(135deg, #1A2F60 0%, #0F172A 100%);
      color: #FFFFFF;
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--color-ink);
    }

    .shamsi-header-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .shamsi-header-icon {
      width: 42px;
      height: 42px;
      background: rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .shamsi-header-title {
      font-size: 15px;
      font-weight: 800;
      color: #FFFFFF;
      margin: 0;
    }

    .shamsi-header-subtitle {
      font-size: 12px;
      color: #93C5FD;
      margin-top: 2px;
      font-weight: 600;
    }

    .shamsi-close-btn {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #FFFFFF;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .shamsi-close-btn:hover {
      background: #E0503F;
      border-color: #E0503F;
      color: #FFFFFF;
    }

    .shamsi-modal-body {
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      overflow-y: auto;
      max-height: calc(92vh - 145px);
    }

    .shamsi-section {
      background: var(--color-paper-card);
      border: 1.5px solid var(--color-ink);
      border-radius: 10px;
      padding: 12px 14px;
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    .shamsi-section-head {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }

    .shamsi-step-badge {
      background: #1A2F60;
      color: #FFFFFF;
      width: 22px;
      height: 22px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 900;
    }

    .shamsi-section-title {
      font-size: 13.5px;
      font-weight: 800;
      color: var(--color-ink);
    }

    .shamsi-section-desc {
      font-size: 11px;
      color: var(--color-ink-muted);
      font-weight: 600;
    }

    /* Date Chips Grid */
    .shamsi-chips-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 6px;
    }

    .shamsi-date-chip {
      background: var(--color-paper-alt);
      border: 1.5px solid var(--color-ink);
      border-radius: 8px;
      padding: 8px 4px;
      text-align: center;
      cursor: pointer;
      transition: all 0.15s ease;
      user-select: none;
    }
    .shamsi-date-chip:hover {
      background: #FFFFFF;
      transform: translateY(-2px);
      box-shadow: 2px 2px 0px var(--color-ink);
    }
    .shamsi-date-chip.active {
      background: #1A2F60;
      color: #FFFFFF;
      border-color: #1A2F60;
      box-shadow: 2px 2px 0px var(--color-ink);
    }
    .shamsi-date-chip-day {
      font-size: 11px;
      font-weight: 600;
      opacity: 0.85;
    }
    .shamsi-date-chip.active .shamsi-date-chip-day {
      color: #93C5FD;
    }
    .shamsi-date-chip-num {
      font-size: 13px;
      font-weight: 900;
      margin-top: 2px;
    }

    /* Time Category & Chips */
    .shamsi-time-category {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    .shamsi-time-label {
      font-size: 11px;
      font-weight: 800;
      color: var(--color-ink-muted);
    }
    .shamsi-time-chips {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
    }
    .shamsi-time-chip {
      background: var(--color-paper-alt);
      border: 1.5px solid var(--color-ink);
      border-radius: 6px;
      padding: 6px 4px;
      font-size: 11px;
      font-weight: 800;
      text-align: center;
      cursor: pointer;
      transition: all 0.15s ease;
      user-select: none;
      direction: ltr;
    }
    .shamsi-time-chip:hover {
      background: #FFFFFF;
      transform: translateY(-1px);
      box-shadow: 2px 2px 0px var(--color-ink);
    }
    .shamsi-time-chip.active {
      background: #0E7C86;
      color: #FFFFFF;
      border-color: #0E7C86;
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    /* Toggle Custom Button */
    .shamsi-toggle-custom-btn {
      background: transparent;
      border: none;
      font-size: 11px;
      font-weight: 700;
      color: #0E7C86;
      cursor: pointer;
      padding: 4px 0;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      text-decoration: underline;
      text-underline-offset: 3px;
      transition: color 0.15s ease;
    }
    .shamsi-toggle-custom-btn:hover {
      color: var(--color-ink);
    }

    /* Custom Input Boxes */
    .shamsi-custom-box {
      background: var(--color-paper-alt);
      border: 1.5px dashed var(--color-ink);
      border-radius: 8px;
      padding: 8px 10px;
      margin: 6px 0;
    }
    .shamsi-inputs-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(85px, 1fr));
      gap: 6px;
    }
    .shamsi-field {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .shamsi-field label {
      font-size: 10px;
      font-weight: 800;
      color: var(--color-ink-muted);
    }
    .shamsi-select, .shamsi-input {
      background: #FFFFFF;
      border: 1.5px solid var(--color-ink);
      border-radius: 6px;
      padding: 5px 6px;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--color-ink);
      outline: none;
    }

    /* Summary Card */
    .shamsi-summary-card {
      background: linear-gradient(135deg, #FAF7EE 0%, #FFFFFF 100%);
      border: 2px solid #1A2F60;
      border-radius: 10px;
      padding: 12px 14px;
      box-shadow: 3px 3px 0px #1A2F60;
    }
    .shamsi-summary-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      flex-wrap: wrap;
      gap: 6px;
    }
    .shamsi-summary-tag {
      font-size: 10.5px;
      font-weight: 800;
      color: #1A2F60;
      background: #E0E7FF;
      padding: 2px 7px;
      border-radius: 4px;
    }
    .shamsi-loc-tag {
      font-size: 10px;
      font-weight: 700;
      color: var(--color-success);
    }
    .shamsi-summary-content {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 0;
    }
    .shamsi-summary-icon {
      font-size: 26px;
      flex-shrink: 0;
    }
    .shamsi-final-date {
      font-size: 14.5px;
      font-weight: 900;
      color: #1A2F60;
    }
    .shamsi-final-time {
      font-size: 13px;
      font-weight: 800;
      color: #0E7C86;
      margin-top: 1px;
    }
    .shamsi-manual-override-box {
      border-top: 1px dashed rgba(26, 47, 96, 0.25);
      margin-top: 8px;
      padding-top: 6px;
    }
    .shamsi-manual-link {
      font-size: 10.5px;
      color: var(--color-ink-muted);
      text-decoration: none;
      font-weight: 600;
    }
    .shamsi-manual-link:hover {
      color: var(--color-ink);
      text-decoration: underline;
    }
    .shamsi-input-manual {
      width: 100%;
      background: #FFFFFF;
      border: 1.5px solid var(--color-ink);
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
      color: var(--color-ink);
      outline: none;
    }

    /* Modal Footer */
    .shamsi-modal-footer {
      padding: 12px 18px;
      background: var(--color-paper-alt);
      border-top: 2px solid var(--color-ink);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    .shamsi-btn-cancel {
      background: #FFFFFF;
      border: 1.5px solid var(--color-ink);
      color: var(--color-ink);
      border-radius: 6px;
      padding: 7px 16px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 2px 2px 0px var(--color-ink);
      transition: all 0.15s ease;
    }
    .shamsi-btn-cancel:hover {
      background: #F3EFE3;
      transform: translateY(-1px);
    }
    .shamsi-btn-submit {
      background: #1A2F60;
      border: 1.5px solid var(--color-ink);
      color: #FFFFFF;
      border-radius: 6px;
      padding: 7px 20px;
      font-size: 12.5px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 2px 2px 0px var(--color-ink);
      transition: all 0.15s ease;
    }
    .shamsi-btn-submit:hover {
      background: #0E7C86;
      transform: translateY(-1px);
      box-shadow: 3px 3px 0px var(--color-ink);
    }
    

    /* Track Filter Segmented Control */
    .track-filter-segmented {
      display: inline-flex;
      align-items: center;
      background: var(--color-paper-alt);
      border: 2px solid var(--color-ink);
      border-radius: 8px;
      padding: 3px;
      gap: 4px;
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    .track-filter-title {
      font-size: 12px;
      font-weight: 800;
      color: var(--color-ink);
      padding: 0 8px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .track-tab-btn {
      background: transparent;
      border: 1.5px solid transparent;
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 12.5px;
      font-weight: 800;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
      color: var(--color-ink);
    }

    .track-tab-btn:hover {
      background: #FFFFFF;
      border-color: var(--color-ink);
    }

    .track-tab-btn.active {
      background: var(--color-ink);
      color: #FFFFFF;
      border-color: var(--color-ink);
      box-shadow: 1.5px 1.5px 0px var(--color-ink);
    }

    .track-tab-btn.ai-tab.active {
      background: #0E7C86;
      color: #FFFFFF;
      border-color: #0E7C86;
    }

    .track-tab-btn.sw-tab.active {
      background: #C0392B;
      color: #FFFFFF;
      border-color: #C0392B;
    }
    
  
    /* ==============================================================
       NEW FEATURES: ANALYTICS, COMPARISON & EMAIL TEMPLATES
       ============================================================== */
    
    /* --- 1. VISUAL ANALYTICS DASHBOARD --- */
    .analytics-hero-banner {
      background: var(--color-paper-card);
      border: 2.5px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      padding: 20px 24px;
      margin-bottom: 22px;
      border-radius: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    .analytics-kpis-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }

    .analytics-kpi-card {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-retro);
      padding: 14px 16px;
      border-radius: 3px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .analytics-kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-card-hover);
    }

    .analytics-kpi-card .kpi-label {
      font-size: 11.5px;
      font-weight: 800;
      color: var(--color-ink-muted);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .analytics-kpi-card .kpi-val {
      font-size: 26px;
      font-weight: 900;
      color: var(--color-ink);
      line-height: 1.15;
    }

    .analytics-kpi-card .kpi-sub {
      font-size: 11px;
      color: var(--color-ink-muted);
      margin-top: 5px;
    }

    .charts-grid-2col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 22px;
      margin-bottom: 24px;
    }

    .chart-card {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      border-radius: 4px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
    }

    .chart-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--color-paper-alt);
      padding-bottom: 10px;
      margin-bottom: 14px;
    }

    .chart-card-title {
      font-size: 15px;
      font-weight: 900;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .chart-wrapper {
      position: relative;
      width: 100%;
      height: 290px;
    }

    .analytics-filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      border-radius: 4px;
      padding: 12px 18px;
      margin-bottom: 22px;
    }

    .analytics-filter-label {
      font-size: 13px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-left: 6px;
      color: var(--color-ink);
    }

    .ana-filter-btn {
      border: 1.5px solid var(--color-ink);
      background: var(--color-paper);
      color: var(--color-ink);
      font-size: 12.5px;
      font-weight: 700;
      font-family: inherit;
      padding: 6px 14px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }

    .ana-filter-btn:hover {
      background: #efe9d9;
      transform: translateY(-1px);
    }

    .ana-filter-btn.active {
      background: var(--color-ink);
      color: #FAF7EE;
      border-color: var(--color-ink);
      box-shadow: 2px 2px 0px rgba(0,0,0,0.18);
    }

    .ana-filter-btn.active .ana-badge {
      background: #FAF7EE;
      color: var(--color-ink);
    }

    .ana-badge {
      font-size: 11px;
      background: var(--color-paper-alt);
      color: var(--color-ink);
      padding: 1px 7px;
      border-radius: 10px;
      font-weight: 800;
    }

    .chart-quick-filter {
      display: inline-flex;
      background: var(--color-paper-alt);
      padding: 3px;
      border-radius: 5px;
      border: 1px solid rgba(26,25,21,0.25);
      gap: 3px;
    }

    .chart-tab-btn {
      border: none;
      background: transparent;
      font-size: 11.5px;
      font-weight: 700;
      font-family: inherit;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.12s ease;
      color: var(--color-ink);
    }

    .chart-tab-btn:hover {
      background: rgba(0,0,0,0.06);
    }

    .chart-tab-btn.active {
      background: var(--color-ink);
      color: #FAF7EE;
      font-weight: 800;
      box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }

    .gpa-stats-pill {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      padding: 8px 14px;
      background: var(--color-paper-alt);
      border: 1px dashed var(--color-ink);
      border-radius: 4px;
      margin-bottom: 12px;
      font-size: 11.5px;
      justify-content: space-between;
      align-items: center;
      line-height: 1.4;
    }

    .gpa-stat-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-weight: 700;
    }

    .gpa-stat-item span.val {
      font-weight: 900;
      color: var(--color-stamp);
      font-size: 12.5px;
    }

    .insights-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
      margin-top: 20px;
    }

    .insight-card {
      background: var(--color-paper-alt);
      border: 1.5px solid var(--color-ink);
      border-radius: 4px;
      padding: 14px 16px;
      box-shadow: 2px 2px 0px var(--color-ink);
    }

    .insight-card-title {
      font-size: 13px;
      font-weight: 900;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .insight-card-desc {
      font-size: 12px;
      line-height: 1.7;
      color: var(--color-ink);
    }

    /* --- 2. HEAD-TO-HEAD COMPARISON --- */
    .compare-floating-bar {
      position: fixed;
      bottom: 22px;
      left: 50%;
      transform: translateX(-50%);
      background: #1A1915;
      color: #FAF7EE;
      border: 2px solid var(--color-gold);
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
      border-radius: 50px;
      padding: 10px 24px;
      z-index: 990;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      min-width: 460px;
      max-width: 92vw;
      animation: slideUpFloat 0.25s ease-out;
    }

    @keyframes slideUpFloat {
      from { transform: translate(-50%, 40px); opacity: 0; }
      to { transform: translate(-50%, 0); opacity: 1; }
    }

    .compare-floating-content {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
    }

    .compare-top-controls {
      background: var(--color-paper-card);
      border: 2px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      padding: 16px 20px;
      border-radius: 4px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }

    .compare-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 20px;
      align-items: start;
    }

    .compare-column {
      background: var(--color-paper-card);
      border: 2.5px solid var(--color-ink);
      box-shadow: var(--shadow-card);
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .compare-col-header {
      padding: 16px 18px;
      border-bottom: 2px solid var(--color-ink);
      background: var(--color-paper-alt);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .compare-col-profile {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .compare-col-monogram {
      width: 46px;
      height: 46px;
      border-radius: 50%;
      color: #fff;
      font-weight: 900;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid var(--color-ink);
      box-shadow: 2px 2px 0px var(--color-ink);
      flex-shrink: 0;
    }

    .compare-block {
      padding: 14px 18px;
      border-bottom: 1.5px solid var(--color-paper-alt);
    }

    .compare-block-title {
      font-size: 11.5px;
      font-weight: 900;
      color: var(--color-ink-muted);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .compare-gpa-box {
      background: #FFF;
      border: 2px solid var(--color-ink);
      border-radius: 4px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .compare-gpa-box.is-winner {
      background: #FEF3C7;
      border-color: #B45309;
      box-shadow: 2px 2px 0px #B45309;
    }

    .winner-crown {
      font-size: 11px;
      font-weight: 800;
      background: #D97706;
      color: #FFFFFF;
      padding: 3px 9px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .skill-tag-shared {
      display: inline-block;
      background: #DCFCE7;
      color: #166534;
      border: 1px solid #86EFAC;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 700;
      margin: 2px;
    }

    .skill-tag-unique {
      display: inline-block;
      background: #EFF6FF;
      color: #1E40AF;
      border: 1px solid #BFDBFE;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 700;
      margin: 2px;
    }

    .compare-checkbox-label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      user-select: none;
      font-size: 11px;
      font-weight: 700;
      background: var(--color-paper);
      border: 1.5px solid var(--color-ink);
      padding: 2px 6px;
      border-radius: 3px;
      transition: all 0.1s ease;
    }

    .compare-checkbox-label:hover {
      background: #FFF;
      box-shadow: 1.5px 1.5px 0px var(--color-ink);
    }

    .compare-checkbox-label input[type="checkbox"] {
      cursor: pointer;
      accent-color: var(--color-gold);
    }

    /* --- 3. EMAIL TEMPLATE GENERATOR MODAL --- */
    .email-templates-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 8px;
    }

    .email-tpl-btn {
      background: #FFFFFF;
      border: 2px solid var(--color-ink);
      border-radius: 4px;
      padding: 10px 12px;
      cursor: pointer;
      text-align: right;
      display: flex;
      align-items: flex-start;
      gap: 8px;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .email-tpl-btn:hover {
      background: var(--color-paper-alt);
      transform: translateY(-1px);
    }

    .email-tpl-btn.active {
      background: #1A1915;
      color: #FFFFFF;
      box-shadow: 2px 2px 0px var(--color-gold);
    }

    .email-tpl-btn .tpl-icon {
      font-size: 18px;
      flex-shrink: 0;
    }

    .email-tpl-btn .tpl-info b {
      display: block;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.3;
    }

    .email-tpl-btn .tpl-info small {
      display: block;
      font-size: 10px;
      opacity: 0.8;
      margin-top: 2px;
    }

    .email-tpl-btn.active .tpl-info small {
      color: #F3EFE3;
    }

  </style>

  <!-- Chart.js for Visual Analytics & SheetJS for Export fallback -->
  <script src="static/chart.min.js"></script>
  <script src="core/static/chart.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js" integrity="sha384-vtjasyidUo0kW94K5MXDXntzOJpQgBKXmE7e2Ga4LG0skTTLeBi97eFAXsqewJjw" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

</head>
<body>

  <!-- TOP HEADER -->
  <header class="top-header">
    <div class="brand-block">
      <div class="brand-badge">__LAB_SHORT__</div>
      <div class="brand-title">
        <h1>
          آزمایشگاه داده‌کاوی
          <span style="font-size: 14px; font-weight: 500; opacity: 0.8;">| دانشگاه علم و صنعت ایران</span>
        </h1>
        <p>پذیرش متقاضیان کارشناسی ارشد ورودی ۱۴۰۵</p>
      </div>
    </div>

    <div class="header-center">
      <div id="liveClock" style="font-size: 13.5px; font-weight: 800; color: #F8FAFC; font-variant-numeric: tabular-nums; background: rgba(255,255,255,0.07); padding: 5px 14px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.12);">
        --:--:--
      </div>
    </div>

    <div class="header-actions">
      <div class="live-indicator" style="background: rgba(220, 38, 38, 0.2); border: 1.5px solid #EF4444; color: #FCA5A5; padding: 4px 12px; border-radius: 4px; font-size: 12.5px; font-weight: 800;">
        <span class="pulse-dot" style="background-color: #EF4444;"></span>
        <span><span id="headerTotalCount">۵۲</span> پرونده موجود</span>
      </div>
      <button class="btn-header primary" onclick="toggleFullscreen()" style="padding: 5px 12px; font-size: 12px;">
        ⛶ تمام‌صفحه
      </button>
    </div>
  </header>

  <!-- TICKER BAND -->
  <div class="ticker-band">
    <span class="ticker-tag">ظرفیت مصوب آزمایشگاه</span>
    <div class="ticker-content">
      <span><b>۴ ظرفیت</b> روزانه نرم‌افزار</span>
      <span style="margin: 0 8px;">·</span>
      <span><b>۲ ظرفیت</b> روزانه هوش مصنوعی</span>
      <span style="margin: 0 8px;">·</span>
      <span><b>۲ ظرفیت</b> شبانه هوش مصنوعی</span>
      <span style="margin: 0 8px;">·</span>
      <span style="color: var(--color-ink-muted); font-size: 11px;">(سهمیه استعدادهای درخشان بر روی ظرفیت روزانه محاسبه می‌گردد)</span>
    </div>
  </div>

  <!-- NAVIGATION TABS -->
  <nav class="nav-tabs-bar">
    <button class="nav-tab-btn active" onclick="switchMainTab('roster', this)">
      📋 کارتابل و بررسی رزومه‌ها
      <span class="tab-badge" id="navSeatsBadge" title="ظرفیت‌های تخصیص‌یافته" style="background: var(--color-success); color: #fff;">۰ / ۸</span>
      <span class="tab-badge" id="navRosterBadge" title="کل داوطلبان">۵۵</span>
    </button>
    <button class="nav-tab-btn" onclick="switchMainTab('files', this)">
      📁 کاوشگر مدارک و رزومه‌ها
    </button>
    <button class="nav-tab-btn" onclick="switchMainTab('analytics', this)">
      📊 آمار و تحلیل دیداری
    </button>
    <button class="nav-tab-btn" onclick="switchMainTab('export', this)">
      📤 گزارش‌گیری
    </button>
  </nav>

  <!-- MAIN CONTAINER -->
  <main class="main-container">

    <!-- UNIFIED TAB: ROSTER, DOSSIERS & CAPACITY SIMULATOR -->
    <section id="tab-roster" class="view-section active">
      
      <!-- COMPACT CAPACITY & SEATS BOARD (2 ROWS: 4 AI + 4 SOFTWARE) -->
      <div class="capacity-compact-box" id="capacityCompactBox">
        <div class="compact-cap-header">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 13.5px; font-weight: 900; color: var(--color-ink);">🏛️ وضعیت ظرفیت مصوب آزمایشگاه (۸ سهمیه):</span>
            <span class="cap-pill ai">🤖 روزانه هوش: <b id="kpiAiRoz">۰ از ۲</b></span>
            <span class="cap-pill shab">🌙 شبانه هوش: <b id="kpiAiShab">۰ از ۲</b></span>
            <span class="cap-pill sw">💻 روزانه نرم‌افزار: <b id="kpiSwRoz">۰ از ۴</b></span>
            <span style="font-size: 11px; color: var(--color-ink-muted);">(سهمیه استعدادهای درخشان بر روی ظرفیت روزانه محاسبه می‌گردد)</span>
          </div>
          <div style="display: flex; gap: 6px; align-items: center;">
            <button class="card-btn" onclick="resetAllSeats()" style="color: var(--color-stamp); font-size: 11px; padding: 2px 8px; font-weight: 800;">
              🔄 خالی‌کردن همه ظرفیت‌ها
            </button>
          </div>
        </div>

        <!-- 8 SEATS IN 2 ROWS: ROW 1 (4 AI), ROW 2 (4 SOFTWARE) -->
        <div class="seats-matrix-wrapper">
          <!-- ROW 1: AI (4 SEATS) -->
          <div class="seats-row-block">
            <div class="seats-row-header">
              <span class="seats-row-badge ai">🤖 گرایش هوش مصنوعی (۴ صندلی)</span>
              <span class="seats-row-sub">۲ صندلی روزانه + ۲ صندلی نوبت دوم (شبانه)</span>
            </div>
            <div class="seats-grid-ai" id="aiSeatsGrid">
              <!-- Populated dynamically: Seats 1, 2, 3, 4 -->
            </div>
          </div>

          <!-- ROW 2: SOFTWARE (4 SEATS) -->
          <div class="seats-row-block">
            <div class="seats-row-header">
              <span class="seats-row-badge sw">💻 گرایش نرم‌افزار (۴ صندلی)</span>
              <span class="seats-row-sub">۴ صندلی روزانه (شامل استعدادهای درخشان)</span>
            </div>
            <div class="seats-grid-sw" id="swSeatsGrid">
              <!-- Populated dynamically: Seats 5, 6, 7, 8 -->
            </div>
          </div>
        </div>
        <div id="compactSeatsGrid" style="display: none;"></div>
      </div>

      <!-- CANDIDATES CONTROLS BAR & ROSTER -->
      <div class="controls-bar" style="flex-direction: column; align-items: stretch; gap: 14px; margin-top: 10px;">
        
        <!-- ROW 1: PRIMARY TRACK SELECTOR & SEARCH/VIEW -->
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; border-bottom: 1.5px solid rgba(26,25,21,0.12); padding-bottom: 12px;">
          
          <!-- DEDICATED TRACK SEGMENTED SWITCH -->
          <div class="track-filter-segmented">
            <span class="track-filter-title">🎯 فیلتر گرایش:</span>
            <button id="btnTrackAll" class="track-tab-btn active" onclick="setTrackFilter('all', this)">
              🌐 همه گرایش‌ها (<span id="trackAllCount">۵۲</span>)
            </button>
            <button id="btnTrackAI" class="track-tab-btn ai-tab" onclick="setTrackFilter('AI', this)">
              🤖 فقط هوش مصنوعی (<span id="trackAiCount">۲۲</span>)
            </button>
            <button id="btnTrackSW" class="track-tab-btn sw-tab" onclick="setTrackFilter('Software', this)">
              💻 فقط نرم‌افزار (<span id="trackSwCount">۳۰</span>)
            </button>
          </div>

          <!-- SEARCH & VIEW MODE -->
          <div class="search-sort-group">
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input type="text" id="searchInput" class="search-input" placeholder="جستجو در نام، دانشگاه، مهارت..." oninput="renderRoster()">
            </div>

            <select id="sortSelect" class="select-sort" onchange="renderRoster()">
              <option value="priority">ترتیب پیش‌فرض (تفکیک گرایش: هوش > نرم‌افزار)</option>
              <option value="sw_first">تفکیک گرایش (نرم‌افزار > هوش)</option>
              <option value="phase">🎯 فاز مصاحبه (فاز ۱ > فاز ۲ > فاز ۳)</option>
              <option value="rank_asc">رتبه کنکور (صعودی / برتر)</option>
              <option value="gpa_desc">معدل کارشناسی (بیشترین)</option>
              <option value="name">نام خانوادگی (الفبا)</option>
              <option value="slot">ساعت جلسه مصاحبه</option>
            </select>

            <div class="view-toggle-btns">
              <button id="btnViewCards" class="view-toggle-btn active" onclick="setViewMode('cards')">📰 کارت‌ها</button>
              <button id="btnViewTable" class="view-toggle-btn" onclick="setViewMode('table')">📊 جدول اکسل</button>
            </div>
          </div>

        </div>

        <!-- ROW 2: STATUS & QUOTA SUB-FILTERS -->
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px;">
          <div class="filters-group">
            <span style="font-size: 11.5px; font-weight: 800; color: var(--color-ink-muted); margin-left: 4px;">فیلتر وضعیت / سهمیه:</span>
            <button class="filter-btn active" onclick="setFilter('all', this)">همه وضعیت‌ها</button>
            <button class="filter-btn accepted-filter" onclick="setFilter('accepted', this)">🌟 پذیرفته‌شدگان در ظرفیت (<span id="filterAcceptedCount">0</span>)</button>
            <button class="filter-btn" style="border-color: #7DD3FC; color: #0284C7; background: #F0F9FF; font-weight: 800;" onclick="setFilter('invited', this)">📅 دعوت‌شده به مصاحبه (<span id="filterInvitedCount">0</span>)</button>
            <button class="filter-btn" style="border-color: #CBD5E1; color: #475569;" onclick="setFilter('pending', this)">⏳ در انتظار بررسی (<span id="filterPendingCount">0</span>)</button>
            <button class="filter-btn" style="border-color: #fca5a5; color: #b91c1c;" onclick="setFilter('rejected', this)">❌ ردشده‌ها (<span id="filterRejectedCount">0</span>)</button>
            <button class="filter-btn" onclick="setFilter('rozaneh', this)">روزانه (<span id="filterRozCount">۳۱</span>)</button>
            <button class="filter-btn" onclick="setFilter('shabaneh', this)">شبانه (<span id="filterShabCount">۳</span>)</button>
            <button class="filter-btn" onclick="setFilter('talented', this)">استعداد درخشان (<span id="filterTalCount">۶</span>)</button>
            <button class="filter-btn" onclick="setFilter('starred', this)">⭐ نشان‌شده‌ها (<span id="filterStarredCount">0</span>)</button>
          </div>
        </div>

        <!-- ROW 3: PHASE PRIORITIZATION SUB-FILTERS -->
        <div class="phase-filter-segmented" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 10px; padding-top: 8px; border-top: 1px dashed #CBD5E1;">
          <span style="font-size: 11.5px; font-weight: 800; color: var(--color-ink-muted); margin-left: 4px;">🎯 فاز اولویت مصاحبه:</span>
          <button id="btnPhaseAll" class="phase-tab-btn active" onclick="setPhaseFilter('all', this)">
            همه فازها (<span id="filterPhaseAllCount">۵۲</span>)
          </button>
          <button id="btnPhase1" class="phase-tab-btn phase-1-btn" onclick="setPhaseFilter('phase1', this)">
            🟣 فاز ۱ (اولویت اول) (<span id="filterPhase1Count">0</span>)
          </button>
          <button id="btnPhase2" class="phase-tab-btn phase-2-btn" onclick="setPhaseFilter('phase2', this)">
            🔵 فاز ۲ (اولویت دوم) (<span id="filterPhase2Count">0</span>)
          </button>
          <button id="btnPhase3" class="phase-tab-btn phase-3-btn" onclick="setPhaseFilter('phase3', this)">
            🟠 فاز ۳ (اولویت سوم) (<span id="filterPhase3Count">0</span>)
          </button>
          <button id="btnPhaseNone" class="phase-tab-btn phase-none-btn" onclick="setPhaseFilter('nophase', this)">
            ⚪ بدون فاز (<span id="filterNoPhaseCount">۵۲</span>)
          </button>
        </div>

      </div>

      <!-- CARDS VIEW HINT BAR -->
      <div id="rosterCardsHintBar" style="background: #F0F9FF; border: 1.5px solid #BAE6FD; border-radius: 6px; padding: 8px 14px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 12px; color: #0369A1; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <span>💡 <b>راهنمای بررسی سریع:</b> با کلیک روی <b>نام متقاضی</b> یا برچسب <b>«📄 جزئیات پرونده ↗»</b> یا هر کجای کارت، پنجره کامل اطلاعات شامل رزومه PDF، متن ایمیل ارسالی، سوابق و فرم ارزیابی باز می‌شود.</span>
        </div>
        <span style="font-weight: 800; color: #0284C7; font-size: 11px; white-space: nowrap;">(امکان کلیک مستقیم روی بدنه کارت)</span>
      </div>

      <div id="rosterCardsContainer" class="candidates-grid"></div>

      <div id="rosterTableContainer" class="table-container" style="display: none;">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 3%; text-align: center;">ردیف</th>
              <th style="width: 13%; text-align: right;">نام و نام خانوادگی</th>
              <th style="width: 8%; text-align: center;">فاز مصاحبه</th>
              <th style="width: 6%; text-align: center;">گرایش</th>
              <th style="width: 9%; text-align: right;">دوره و سهمیه</th>
              <th style="width: 5%; text-align: center;">رتبه ارشد</th>
              <th style="width: 11%; text-align: right;">دانشگاه کارشناسی</th>
              <th style="width: 5%; text-align: center;">معدل</th>
              <th style="width: 12%; text-align: center;">وضعیت قبولی / مصاحبه</th>
              <th style="width: 11%; text-align: center;">زمان مصاحبه</th>
              <th style="width: 11%; text-align: center;">اقدام (قبول / دعوت / رد)</th>
              <th style="width: 6%; text-align: center;">پرونده</th>
            </tr>
          </thead>
          <tbody id="rosterTableBody"></tbody>
        </table>
      </div>
    </section>

    <!-- TAB 2: FILES -->
    <section id="tab-files" class="view-section">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; border-bottom: 2px solid var(--color-ink); padding-bottom: 10px;">
        <div>
          <h2 style="font-size: 19px; font-weight: 900; margin: 0 0 4px 0;">📁 کاوشگر مدارک، فایل‌های PDF و رزومه‌های متقاضیان</h2>
          <div style="font-size: 11.5px; color: var(--color-ink-muted);">مرتب‌سازی پیش‌فرض بر اساس تفکیک گرایش (هوش مصنوعی > نرم‌افزار) جهت پیگیری سریع پرونده‌ها</div>
        </div>

        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
          <div class="track-filter-segmented" style="height: 34px;">
            <button class="track-btn active" id="btnFilesFilterAll" onclick="setFilesTrackFilter('all')">همه (۵۵)</button>
            <button class="track-btn" id="btnFilesFilterAI" onclick="setFilesTrackFilter('AI')">🤖 هوش مصنوعی (۲۲)</button>
            <button class="track-btn" id="btnFilesFilterSW" onclick="setFilesTrackFilter('Software')">💻 نرم‌افزار (۳۳)</button>
          </div>
          <div class="search-box" style="width: 250px;">
            <span class="search-icon">🔍</span>
            <input type="text" id="filesSearchInput" class="search-input" placeholder="جستجو در نام، گرایش، فایل..." oninput="renderFilesExplorer()">
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 3%; text-align: center;">ردیف</th>
              <th style="width: 14%; text-align: right;">نام متقاضی</th>
              <th style="width: 8%; text-align: center;">گرایش</th>
              <th style="width: 14%; text-align: left;">پوشه فایل‌ها</th>
              <th style="width: 35%;">فایل‌های مدارک و رزومه</th>
              <th style="width: 11%;">سایر ضمائم</th>
              <th style="width: 7%; text-align: center;">متن ایمیل</th>
              <th style="width: 8%; text-align: center;">عملیات</th>
            </tr>
          </thead>
          <tbody id="filesTableBody"></tbody>
        </table>
      </div>
    </section>

    <!-- TAB 5: VISUAL ANALYTICS DASHBOARD -->
    <section id="tab-analytics" class="view-section">
      <div class="analytics-hero-banner">
        <div>
          <h2 style="font-size: 20px; font-weight: 900; display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span>📊</span>
            <span>داشبورد آماری و تحلیل هوشمند پذیرش کارشناسی ارشد ورودی ۱۴۰۵</span>
          </h2>
          <p style="font-size: 13px; color: var(--color-ink-muted);">
            __LAB_NAME__ (__LAB_SHORT__) - __DEPARTMENT__ __INSTITUTION__ | استاد راهنما: __SUPERVISOR__
          </p>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="card-btn primary" onclick="renderAnalytics()">🔄 بروزرسانی نمودارها</button>
        </div>
      </div>

      <!-- ANALYTICS FILTER BAR -->
      <div class="analytics-filter-bar">
        <div class="analytics-filter-label">
          <span>🔍</span>
          <span>فیلتر جامعه آماری:</span>
        </div>
        <button class="ana-filter-btn active" data-filter="all" onclick="setAnalyticsFilter('all', this)">
          <span>همه متقاضیان</span>
          <span class="ana-badge" id="anaBadgeAll">۵۵</span>
        </button>
        <button class="ana-filter-btn" data-filter="ai" onclick="setAnalyticsFilter('ai', this)">
          <span>🤖 هوش مصنوعی</span>
          <span class="ana-badge" id="anaBadgeAi">۲۲</span>
        </button>
        <button class="ana-filter-btn" data-filter="sw" onclick="setAnalyticsFilter('sw', this)">
          <span>💻 نرم‌افزار</span>
          <span class="ana-badge" id="anaBadgeSw">۳۳</span>
        </button>
        <button class="ana-filter-btn" data-filter="talented" onclick="setAnalyticsFilter('talented', this)">
          <span>🏆 استعداد درخشان</span>
          <span class="ana-badge" id="anaBadgeTal">۱۴</span>
        </button>
        <button class="ana-filter-btn" data-filter="rozaneh" onclick="setAnalyticsFilter('rozaneh', this)">
          <span>🎓 روزانه آزمون</span>
          <span class="ana-badge" id="anaBadgeRoz">۳۱</span>
        </button>
        <button class="ana-filter-btn" data-filter="shabaneh" onclick="setAnalyticsFilter('shabaneh', this)">
          <span>🌙 نوبت دوم (شبانه)</span>
          <span class="ana-badge" id="anaBadgeShab">۳</span>
        </button>
      </div>

      <!-- ROW 1: KPIS GRID -->
      <div class="analytics-kpis-grid">
        <div class="analytics-kpi-card">
          <div class="kpi-label">👥 کل متقاضیان فیلترشده</div>
          <div class="kpi-val" id="statTotalCands">۵۵</div>
          <div class="kpi-sub">پرونده فعال در این جامعه آماری</div>
        </div>
        <div class="analytics-kpi-card">
          <div class="kpi-label" style="color: var(--color-ai);">🤖 گرایش هوش مصنوعی</div>
          <div class="kpi-val" style="color: var(--color-ai);" id="statAiCands">۲۲</div>
          <div class="kpi-sub" id="statAiSub">۴۰.۰٪ جامعه آماری</div>
        </div>
        <div class="analytics-kpi-card">
          <div class="kpi-label" style="color: var(--color-sw);">💻 نرم‌افزار</div>
          <div class="kpi-val" style="color: var(--color-sw);" id="statSwCands">۳۳</div>
          <div class="kpi-sub" id="statSwSub">۶۰.۰٪ جامعه آماری</div>
        </div>
        <div class="analytics-kpi-card">
          <div class="kpi-label" style="color: var(--color-gold);">🏆 سهمیه استعداد درخشان</div>
          <div class="kpi-val" style="color: var(--color-gold);" id="statTalCands">۱۴</div>
          <div class="kpi-sub">پذیرش بدون آزمون</div>
        </div>
        <div class="analytics-kpi-card">
          <div class="kpi-label" style="color: var(--color-success);">🪑 تخصیص ظرفیت صندلی‌ها</div>
          <div class="kpi-val" style="color: var(--color-success);" id="statAssignedSeats">۰ / ۸</div>
          <div class="kpi-sub">صندلی قطعی آزمایشگاه</div>
        </div>
        <div class="analytics-kpi-card">
          <div class="kpi-label" style="color: var(--color-stamp);">🎓 میانگین معدل کارشناسی</div>
          <div class="kpi-val" style="color: var(--color-stamp);" id="statAvgGpa">۱۷.۸۱</div>
          <div class="kpi-sub">از نمره کل ۲۰</div>
        </div>
      </div>

      <!-- ROW 2: CHARTS (UNIS & GPA) -->
      <div class="charts-grid-2col">
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">
              <span>🏛️</span>
              <span>توزیع دانشگاه‌های مقطع کارشناسی</span>
            </div>
            <div class="chart-quick-filter">
              <button class="chart-tab-btn active" data-chart="unis" data-track="all" onclick="setQuickTrackFilter('unis', 'all', this)">همه</button>
              <button class="chart-tab-btn" data-chart="unis" data-track="AI" onclick="setQuickTrackFilter('unis', 'AI', this)">هوش مصنوعی</button>
              <button class="chart-tab-btn" data-chart="unis" data-track="Software" onclick="setQuickTrackFilter('unis', 'Software', this)">نرم‌افزار</button>
            </div>
          </div>
          <div class="chart-wrapper" style="height: 330px;">
            <canvas id="chartUnisCanvas"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">
              <span>📈</span>
              <span>توزیع دقیق بازه‌های معدل کارشناسی</span>
            </div>
            <div class="chart-quick-filter">
              <button class="chart-tab-btn active" data-chart="gpa" data-track="all" onclick="setQuickTrackFilter('gpa', 'all', this)">همه</button>
              <button class="chart-tab-btn" data-chart="gpa" data-track="AI" onclick="setQuickTrackFilter('gpa', 'AI', this)">هوش مصنوعی</button>
              <button class="chart-tab-btn" data-chart="gpa" data-track="Software" onclick="setQuickTrackFilter('gpa', 'Software', this)">نرم‌افزار</button>
            </div>
          </div>
          <div id="gpaDetailedStatsPill" class="gpa-stats-pill">
            <!-- Dynamically populated stats: Avg, Max, Min, Median, Count -->
          </div>
          <div class="chart-wrapper" style="height: 290px;">
            <canvas id="chartGpaCanvas"></canvas>
          </div>
        </div>
      </div>

      <!-- ROW 3: DETAILED LAB QUOTAS & CAPACITY ANALYSIS (FULL-WIDTH ENHANCED CHART) -->
      <div class="chart-card" style="margin-top: 18px;">
        <div class="chart-card-header">
          <div>
            <div class="chart-card-title">
              <span>🎯</span>
              <span>تحلیل تفکیکی سهمیه‌ها و ظرفیت پذیرش __LAB_NAME__</span>
            </div>
            <div style="font-size: 11.5px; color: var(--color-ink-muted); margin-top: 3px;">
              ورودی‌های ارشد ۱۴۰۵: ۴ سهمیه روزانه نرم‌افزار + ۲ سهمیه روزانه هوش مصنوعی + ۲ سهمیه شبانه هوش مصنوعی (استعدادهای درخشان بر روی ظرفیت روزانه محاسبه می‌شوند)
            </div>
          </div>
          <div class="chart-quick-filter">
            <button class="chart-tab-btn active" id="btnQuotaViewCapacity" onclick="switchQuotaChartView('capacity')">📊 ظرفیت، پذیرش و تقاضا</button>
            <button class="chart-tab-btn" id="btnQuotaViewBreakdown" onclick="switchQuotaChartView('breakdown')">🥧 ترکیب سهمیه‌ها (روزانه / استعداد / شبانه)</button>
          </div>
        </div>

        <!-- SUMMARY METRICS STRIP -->
        <div class="quota-summary-strip" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin: 14px 0 16px 0;">
          <div style="background: #FFF5F5; border: 1.5px solid #FEB2B2; border-right: 4px solid var(--color-sw); padding: 10px 14px; border-radius: 4px;">
            <div style="font-size: 13px; font-weight: 800; color: var(--color-sw); margin-bottom: 4px;">💻 روزانه نرم‌افزار (۴ سهمیه مصوب)</div>
            <div style="font-size: 11.5px; color: var(--color-ink-muted); line-height: 1.7;">
              پذیرفته‌شده: <b id="stripSwRozAssigned" style="color: var(--color-success); font-size: 13px;">۰</b> از ۴ | فاز ۱: <b id="stripSwRozPhase1">۱۳</b> نفر | کل متقاضیان: <b>۳۳</b> نفر (۲۳ روزانه + ۱۰ استعداد)
            </div>
          </div>

          <div style="background: #F0FDFA; border: 1.5px solid #99F6E4; border-right: 4px solid var(--color-ai); padding: 10px 14px; border-radius: 4px;">
            <div style="font-size: 13px; font-weight: 800; color: var(--color-ai); margin-bottom: 4px;">🤖 روزانه هوش مصنوعی (۲ سهمیه مصوب)</div>
            <div style="font-size: 11.5px; color: var(--color-ink-muted); line-height: 1.7;">
              پذیرفته‌شده: <b id="stripAiRozAssigned" style="color: var(--color-success); font-size: 13px;">۰</b> از ۲ | فاز ۱: <b id="stripAiRozPhase1">۹</b> نفر | کل متقاضیان: <b>۱۹</b> نفر (۱۵ روزانه + ۴ استعداد)
            </div>
          </div>

          <div style="background: #FAF5FF; border: 1.5px solid #E9D5FF; border-right: 4px solid var(--color-shabaneh); padding: 10px 14px; border-radius: 4px;">
            <div style="font-size: 13px; font-weight: 800; color: var(--color-shabaneh); margin-bottom: 4px;">🌙 شبانه هوش مصنوعی (۲ سهمیه مصوب)</div>
            <div style="font-size: 11.5px; color: var(--color-ink-muted); line-height: 1.7;">
              پذیرفته‌شده: <b id="stripAiShabAssigned" style="color: var(--color-success); font-size: 13px;">۰</b> از ۲ | فاز ۱: <b id="stripAiShabPhase1">۲</b> نفر | کل متقاضیان: <b>۳</b> نفر شبانه
            </div>
          </div>
        </div>

        <div class="chart-wrapper" style="height: 380px;">
          <canvas id="chartQuotaCanvas"></canvas>
        </div>
      </div>
    </section>


    <!-- TAB 7: EXPORT STUDIO -->
    <section id="tab-export" class="view-section">
      
      <!-- HERO HEADER & PRESETS -->
      <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 22px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 18px;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
              <span style="font-size: 26px;">📤</span>
              <h2 style="font-size: 22px; font-weight: 900; margin: 0; color: var(--color-ink);">
                مرکز جامع گزارش‌گیری و خروجی سفارشی
              </h2>
            </div>
            <p style="font-size: 13.5px; color: var(--color-ink-muted); margin: 0; line-height: 1.7;">
              فیلتر دلخواه متقاضیان بر اساس فاز، گرایش، دوره پذیرش، دانشگاه و وضعیت؛ انتخاب سفارشی ستون‌های داده و دریافت مستقیم خروجی اکسل واقعی (.XLSX)، فایل متنی CSV، فرم چاپی سربرگ‌دار رسمی PDF یا کپی در کلیپ‌بورد.
            </p>
          </div>
          <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <a href="/download/New Member Lab.xlsx" class="card-btn" download style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; font-weight: 800; font-size: 12px; text-decoration: none; background: #FFF; border: 1.5px solid var(--color-ink); box-shadow: 2px 2px 0 var(--color-ink);">
              📥 دانلود اکسل خام متقاضیان
            </a>
            <a href="/download/applicants_summary.xlsx" class="card-btn" download style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; font-weight: 800; font-size: 12px; text-decoration: none; background: #FFF; border: 1.5px solid var(--color-ink); box-shadow: 2px 2px 0 var(--color-ink);">
              ⏱️ دانلود اکسل زمان‌بندی جلسات
            </a>
          </div>
        </div>

        <!-- PRESETS ROW -->
        <div style="background: var(--color-paper); border: 1.5px dashed var(--color-ink); padding: 12px 16px; border-radius: 4px;">
          <div style="font-size: 12px; font-weight: 800; color: var(--color-ink); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>⚡</span>
            <span>پیکربندی‌ها و الگوهای خروجی آماده (Quick Presets - با یک کلیک):</span>
          </div>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            <button class="export-preset-btn" onclick="applyExportPreset('phase1')">
              🟣 داوطلبان فاز ۱ (اولویت اول)
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('phase2')">
              🔵 داوطلبان فاز ۲ (اولویت دوم)
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('phase3')">
              🟠 داوطلبان فاز ۳ (اولویت سوم)
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('phase12')">
              🎯 فاز ۱ و ۲ همزمان
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('accepted')">
              🌟 پذیرفته‌شدگان قطعی در ظرفیت
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('invited')">
              📅 کلیه دعوت‌شدگان به مصاحبه
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('interview_tuesday')" style="background:#FEF3C7; color:#92400E; border-color:#D97706;">
              🗓️ سه‌شنبه ۱۹ آبان (نرم‌افزار)
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('interview_wednesday')" style="background:#E0F2FE; color:#0369A1; border-color:#0284C7;">
              🗓️ چهارشنبه ۲۰ آبان (هوش مصنوعی)
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('interview_saturday')" style="background:#F3E8FF; color:#6D28D9; border-color:#7C3AED;">
              🗓️ شنبه ۲۴ آبان
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('talented')">
              🏆 سهمیه استعدادهای درخشان
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('contacts')">
              📞 فهرست تماس و هماهنگی
            </button>
            <button class="export-preset-btn" onclick="applyExportPreset('all_data')">
              📑 گزارش کامل تمام پرونده‌ها (۲۲ ستون)
            </button>
          </div>
        </div>
      </div>

      <!-- FILTER & COLUMN CONFIGURATION GRID -->
      <div style="display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; margin-bottom: 24px;">
        
        <!-- PANEL 1: MULTI-DIMENSIONAL FILTERS -->
        <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px; display: flex; flex-direction: column; gap: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid var(--color-ink); padding-bottom: 8px;">
            <h3 style="font-size: 15px; font-weight: 900; margin: 0; display: flex; align-items: center; gap: 6px;">
              <span>🎯</span>
              <span>بخش ۱: فیلترهای چندگانه و هوشمند داوطلبان</span>
            </h3>
            <button class="card-btn" style="padding: 2px 8px; font-size: 11px;" onclick="resetExportFilters()">
              🔄 بازنشانی فیلترها
            </button>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
            
            <!-- Filter: Track -->
            <div class="form-group">
              <label for="expFilterTrack" style="font-weight: 800;">🎓 گرایش کارشناسی ارشد:</label>
              <select id="expFilterTrack" class="form-control" onchange="onExportFilterChange()">
                <option value="all">🌐 همه گرایش‌ها (هوش و نرم‌افزار)</option>
                <option value="AI">🤖 فقط هوش مصنوعی</option>
                <option value="Software">💻 فقط نرم‌افزار</option>
              </select>
            </div>

            <!-- Filter: Phase -->
            <div class="form-group">
              <label for="expFilterPhase" style="font-weight: 800;">🎯 فاز اولویت مصاحبه:</label>
              <select id="expFilterPhase" class="form-control" style="font-weight: 800;" onchange="onExportFilterChange()">
                <option value="all">همه فازها</option>
                <option value="phase1" style="color: #6D28D9; font-weight: 800;">🟣 فقط فاز ۱ (اولویت اول)</option>
                <option value="phase2" style="color: #0369A1; font-weight: 800;">🔵 فقط فاز ۲ (اولویت دوم)</option>
                <option value="phase3" style="color: #B45309; font-weight: 800;">🟠 فقط فاز ۳ (اولویت سوم)</option>
                <option value="phase12">🟣🔵 فاز ۱ و ۲ همزمان</option>
                <option value="nophase">⚪ بدون فاز (تعیین‌نشده)</option>
              </select>
            </div>

            <!-- Filter: Admission / Quota -->
            <div class="form-group">
              <label for="expFilterAdmission" style="font-weight: 800;">🏛️ دوره و نوع سهمیه پذیرش:</label>
              <select id="expFilterAdmission" class="form-control" onchange="onExportFilterChange()">
                <option value="all">همه دوره‌ها و سهمیه‌ها</option>
                <option value="rozaneh">روزانه (سهمیه آزاد / مستقیم)</option>
                <option value="shabaneh">شبانه (نوبت دوم)</option>
                <option value="talented">استعدادهای درخشان (بدون آزمون)</option>
              </select>
            </div>

            <!-- Filter: Status -->
            <div class="form-group">
              <label for="expFilterStatus" style="font-weight: 800;">⚡ وضعیت قبولی / بررسی:</label>
              <select id="expFilterStatus" class="form-control" onchange="onExportFilterChange()">
                <option value="all">همه وضعیت‌ها</option>
                <option value="accepted">🌟 پذیرفته‌شده قطعی (دارای صندلی در آزمایشگاه)</option>
                <option value="invited">📅 دعوت‌شده به جلسه مصاحبه</option>
                <option value="pending">⏳ در انتظار بررسی</option>
                <option value="rejected">❌ رد شده / انصراف داده شده</option>
              </select>
            </div>

            <!-- Filter: Interview Date -->
            <div class="form-group">
              <label for="expFilterInterviewDate" style="font-weight: 800;">📅 تاریخ و روز جلسه مصاحبه:</label>
              <select id="expFilterInterviewDate" class="form-control" onchange="onExportFilterChange()" style="font-weight: 700;">
                <option value="all">همه روزها و تاریخ‌های مصاحبه</option>
                <option value="has_date">📋 کلیه مصاحبه‌شوندگان (دارای زمان مصاحبه)</option>
                <option value="۱۹ آبان">🗓️ سه‌شنبه ۱۹ آبان ۱۴۰۵ (نرم‌افزار)</option>
                <option value="۲۰ آبان">🗓️ چهارشنبه ۲۰ آبان ۱۴۰۵ (هوش مصنوعی)</option>
                <option value="۲۴ آبان">🗓️ شنبه ۲۴ آبان ۱۴۰۵</option>
                <option value="no_date">⚪ بدون تاریخ مصاحبه</option>
              </select>
            </div>

            <!-- Filter: Min GPA -->
            <div class="form-group">
              <label for="expFilterMinGpa" style="font-weight: 800;">📊 شرط حداقل معدل کارشناسی:</label>
              <select id="expFilterMinGpa" class="form-control" onchange="onExportFilterChange()">
                <option value="0">بدون شرط معدل (همه)</option>
                <option value="16">معدل ۱۶.۰۰ به بالا</option>
                <option value="17">معدل ۱۷.۰۰ به بالا (بسیار خوب)</option>
                <option value="18">معدل ۱۸.۰۰ به بالا (ممتاز و شاگرد اول)</option>
                <option value="19">معدل ۱۹.۰۰ به بالا (نخبگان)</option>
              </select>
            </div>

            <!-- Filter: Arshad Rank -->
            <div class="form-group">
              <label for="expFilterRank" style="font-weight: 800;">🏅 رتبه کنکور کارشناسی ارشد:</label>
              <select id="expFilterRank" class="form-control" onchange="onExportFilterChange()">
                <option value="all">همه رتبه‌ها</option>
                <option value="50">رتبه‌های برتر کشوری (زیر ۵۰)</option>
                <option value="100">رتبه‌های دورقمی (زیر ۱۰۰)</option>
                <option value="200">رتبه‌های زیر ۲۰۰</option>
              </select>
            </div>

            <!-- Filter: University -->
            <div class="form-group">
              <label for="expFilterUni" style="font-weight: 800;">🏫 دانشگاه مقطع کارشناسی:</label>
              <select id="expFilterUni" class="form-control" onchange="onExportFilterChange()">
                <option value="all">همه دانشگاه‌ها</option>
                <option value="علم و صنعت">دانشگاه علم و صنعت ایران (IUST)</option>
                <option value="خواجه نصیر">صنعتی خواجه نصیرالدین طوسی</option>
                <option value="شهید بهشتی">دانشگاه شهید بهشتی</option>
                <option value="شریف">صنعتی شریف</option>
                <option value="امیرکبیر">صنعتی امیرکبیر (پلی‌تکنیک)</option>
                <option value="صنعتی اصفهان">صنعتی اصفهان (IUT)</option>
                <option value="نوشیروانی بابل">صنعتی نوشیروانی بابل</option>
                <option value="علامه طباطبائی">دانشگاه علامه طباطبائی</option>
                <option value="خوارزمی">دانشگاه خوارزمی</option>
                <option value="فردوسی مشهد">دانشگاه فردوسی مشهد</option>
                <option value="تبریز">دانشگاه تبریز</option>
                <option value="چمران">شهید چمران اهواز</option>
                <option value="بوعلی سینا">بوعلی سینا همدان</option>
              </select>
            </div>

            <!-- Filter: Starred only -->
            <div class="form-group">
              <label for="expFilterStarred" style="font-weight: 800;">⭐ متقاضیان نشان‌شده:</label>
              <select id="expFilterStarred" class="form-control" onchange="onExportFilterChange()">
                <option value="all">همه پرونده‌ها</option>
                <option value="starred">★ فقط داوطلبان نشان‌شده (ستاره‌دار)</option>
              </select>
            </div>

          </div>

          <!-- Free text search -->
          <div class="form-group">
            <label for="expSearchQuery" style="font-weight: 800;">🔍 جستجوی کلیدواژه، نام، مهارت، دبیرستان:</label>
            <input type="text" id="expSearchQuery" class="form-control" placeholder="مثلاً: سمپاد، RAG، پایتون، لنگرودی، مهیمن..." oninput="onExportFilterChange()">
          </div>

        </div>

        <!-- PANEL 2: COLUMN CUSTOMIZER -->
        <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px; display: flex; flex-direction: column;">
          
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid var(--color-ink); padding-bottom: 8px; margin-bottom: 12px;">
            <h3 style="font-size: 15px; font-weight: 900; margin: 0; display: flex; align-items: center; gap: 6px;">
              <span>📋</span>
              <span>بخش ۲: انتخاب ستون‌های داده در فایل خروجی</span>
            </h3>
            <span id="colCountBadge" class="badge-pill" style="background:#E0F2FE; color:#0369A1; font-size:11px;">
              ۱۱ ستون فعال
            </span>
          </div>

          <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
            <button class="card-btn" style="padding: 2px 7px; font-size: 10.5px;" onclick="setAllColumns(true)">✓ انتخاب همه</button>
            <button class="card-btn" style="padding: 2px 7px; font-size: 10.5px;" onclick="setAllColumns(false)">✕ لغو همه</button>
            <button class="card-btn primary" style="padding: 2px 7px; font-size: 10.5px;" onclick="setStandardColumns()">⭐ ستون‌های استاندارد</button>
            <button class="card-btn" style="padding: 2px 7px; font-size: 10.5px;" onclick="setContactColumns()">📞 فقط تماس</button>
            <button class="card-btn" style="padding: 2px 7px; font-size: 10.5px;" onclick="setEvalColumns()">✍️ فقط ارزیابی و مصاحبه</button>
          </div>

          <!-- CHECKBOXES CONTAINER -->
          <div id="exportColumnsContainer" style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; overflow-y: auto; max-height: 380px; padding-left: 4px;">
            <!-- Injected by JS -->
          </div>

        </div>

      </div>

      <!-- EXPORT ACTIONS BAR -->
      <div style="background: #FFFBEB; border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 18px 24px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="background: var(--color-ink); color: #fff; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
            📊
          </div>
          <div>
            <div style="font-size: 15px; font-weight: 900; color: var(--color-ink);" id="exportStatsSummary">
              تعداد رکوردهای منطبق: ۵۲ داوطلب (از ۵۲ نفر) · ۱۱ ستون
            </div>
            <div style="font-size: 12px; color: var(--color-ink-muted);" id="exportFilterDescSummary">
              فیلتر فعال: همه گرایش‌ها · همه فازها · همه سهمیه‌ها
            </div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button class="card-btn" style="background: #15803D; color: #fff; border-color: #166534; font-weight: 800; font-size: 13px; padding: 10px 18px;" onclick="executeExport('excel')">
            📥 خروجی اکسل پیشرفته (.XLSX)
          </button>
          <button class="card-btn" style="background: #0284C7; color: #fff; border-color: #0369A1; font-weight: 800; font-size: 13px; padding: 10px 18px;" onclick="executeExport('csv')">
            📄 خروجی فایل متنی CSV
          </button>
          <button class="card-btn" style="background: #C0392B; color: #fff; border-color: #991B1B; font-weight: 800; font-size: 13px; padding: 10px 18px;" onclick="executeExport('pdf')">
            📥 دریافت خروجی PDF رسمی (.PDF)
          </button>
          <button class="card-btn" style="background: #FFFFFF; color: var(--color-ink); font-weight: 800; font-size: 13px; padding: 10px 14px;" onclick="executeExport('copy')" title="کپی جدول برای Paste مستقیم در اکسل یا تلگرام">
            📋 کپی در کلیپ‌بورد
          </button>
        </div>

      </div>

      <!-- LIVE PREVIEW TABLE -->
      <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 16px; font-weight: 900; margin: 0; display: flex; align-items: center; gap: 8px;">
            <span>👁️</span>
            <span>پیش‌نمایش زنده خروجی</span>
          </h3>
          <span style="font-size: 12px; color: var(--color-ink-muted);">
            این جدول دقیقاً مطابق با فایل نهایی که دانلود خواهید کرد رندر شده است.
          </span>
        </div>

        <div class="table-container" style="max-height: 520px; overflow: auto; border: 1.5px solid var(--color-ink);">
          <table class="excel-table" id="exportPreviewTable">
            <thead id="exportPreviewHead"></thead>
            <tbody id="exportPreviewBody"></tbody>
          </table>
        </div>
      </div>

    </section>

  </main>

  <div id="printableReportArea" style="display: none;"></div>

  <!-- MODAL: DOSSIER DRAWER -->
  <div id="dossierModalOverlay" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modalName" onclick="handleModalOverlayClick(event)">
    <div class="dossier-modal">
      <div class="modal-header">
        <div class="modal-candidate-profile">
          <div id="modalMonogram" class="modal-monogram">--</div>
          <div class="modal-title-box">
            <h2 id="modalName">نام متقاضی</h2>
            <p id="modalSubtitle">گرایش هوش مصنوعی | روزانه استعداد درخشان</p>
          </div>
        </div>
        <button class="modal-close-btn" onclick="closeDossierModal()">✕</button>
      </div>

      <div style="padding: 10px 24px; background: #FFF9E6; border-bottom: 1.5px solid var(--color-ink); display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 12px; font-weight: 700; color: #854D0E;">✉️ ارسال ایمیل و مکاتبه رسمی با این متقاضی:</span>
        <button type="button" class="card-btn primary" style="padding: 3px 12px; font-size: 11.5px;" onclick="openEmailModal(selectedCandidate.id)">
          ✉️ باز کردن قالب‌ساز خودکار ایمیل
        </button>
      </div>
      <div class="modal-tabs-bar">
        <button class="modal-tab-btn active" onclick="switchModalTab('overview', this)">
          📑 خلاصه سوابق و مشخصات
        </button>
        <button class="modal-tab-btn" onclick="switchModalTab('pdf', this)">
          📄 مشاهده زنده رزومه
        </button>
        <button class="modal-tab-btn" onclick="switchModalTab('email', this)">
          ✉️ متن کامل ایمیل ارسالی (main.txt)
        </button>
        <button class="modal-tab-btn" onclick="switchModalTab('eval', this)">
          ✍️ ارزیابی، پذیرش و تخصیص ظرفیت
        </button>
      </div>

      <div class="modal-body">
        
        <!-- PANE 1: OVERVIEW -->
        <div id="modalPane-overview" class="modal-tab-pane active">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px;">
              <h3 style="font-size: 15px; font-weight: 800; margin-bottom: 12px; border-bottom: 1.5px solid var(--color-paper-alt); padding-bottom: 6px;">🎓 سوابق تحصیلی و اطلاعات تماس</h3>
              <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                <div class="card-info-row">
                  <span class="info-label">شماره تماس:</span>
                  <span id="modalPhone" class="info-val" dir="ltr" style="direction: ltr; display: inline-block; font-weight: 700;">--</span>
                  <button class="quick-copy-btn" onclick="copyContactText(document.getElementById('modalPhone').textContent)">کپی</button>
                </div>
                <div class="card-info-row">
                  <span class="info-label">ایمیل:</span>
                  <span id="modalEmail" class="info-val" dir="ltr" style="direction: ltr; display: inline-block;">--</span>
                  <button class="quick-copy-btn" onclick="copyContactText(document.getElementById('modalEmail').textContent)">کپی</button>
                </div>
                <div class="card-info-row">
                  <span class="info-label">لینک‌ها:</span>
                  <span id="modalSocial" class="info-val">--</span>
                </div>
                <div class="card-info-row">
                  <span class="info-label">کارشناسی:</span>
                  <span id="modalBsc" class="info-val">--</span>
                </div>
                <div class="card-info-row">
                  <span class="info-label">معدل کارشناسی:</span>
                  <span id="modalGpa" class="info-val" style="color: var(--color-stamp); font-size: 15px;">--</span>
                </div>
                <div class="card-info-row">
                  <span class="info-label">رتبه کنکور:</span>
                  <span id="modalKonkur" class="info-val">--</span>
                </div>
                <div class="card-info-row">
                  <span class="info-label">دبیرستان:</span>
                  <span id="modalHighSchool" class="info-val">--</span>
                </div>
              </div>
            </div>

            <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px;">
              <h3 style="font-size: 15px; font-weight: 800; margin-bottom: 12px; border-bottom: 1.5px solid var(--color-paper-alt); padding-bottom: 6px;">⚡ وضعیت پذیرش در ظرفیت آزمایشگاه</h3>
              <div style="display: flex; flex-direction: column; gap: 12px; font-size: 13px;">
                <div id="modalSeatStatusBox" style="padding: 12px; background: var(--color-paper-alt); border: 1.5px solid var(--color-ink);">
                  <!-- Injected by JS -->
                </div>
                <div>
                  <div style="font-weight: 700; color: var(--color-ink-muted); margin-bottom: 6px;">فریم‌ورک‌ها و ابزارها:</div>
                  <div id="modalSkillsTags" class="skills-tags-row"></div>
                </div>
                <div>
                  <div style="font-weight: 700; color: var(--color-ink-muted); margin-bottom: 4px;">سوابق کاری، پژوهشی و TA:</div>
                  <p id="modalExp" style="line-height: 1.6; font-weight: 600;"></p>
                </div>
              </div>
            </div>
          </div>

          <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 16px; margin-top: 20px;">
            <h3 style="font-size: 15px; font-weight: 800; margin-bottom: 8px;">🎯 علاقه‌مندی‌های پژوهشی و حوزه پایان‌نامه</h3>
            <p id="modalInterests" style="font-size: 14px; line-height: 1.8; font-weight: 600;"></p>
          </div>

          <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 16px; margin-top: 16px;">
            <h3 style="font-size: 15px; font-weight: 800; margin-bottom: 8px;">📝 نکات تکمیلی و ارزیابی اولیه پرونده</h3>
            <p id="modalNotes" style="font-size: 13px; line-height: 1.7; color: var(--color-ink-muted);"></p>
          </div>
        </div>

        <!-- PANE 2: PDF VIEWER -->
        <div id="modalPane-pdf" class="modal-tab-pane">
          <div class="pdf-actions-row">
            <div class="pdf-selector-btns" id="pdfSelectorBtns"></div>
            <div>
              <a id="btnDownloadCurrentPdf" href="#" class="card-btn primary" target="_blank" download>
                📥 دانلود مستقیم PDF
              </a>
            </div>
          </div>
          <iframe id="pdfIframe" class="pdf-viewer-frame" src=""></iframe>
        </div>

        <!-- PANE 3: EMAIL READER -->
        <div id="modalPane-email" class="modal-tab-pane">
          <div class="email-container">
            <div class="email-header-meta">
              <div class="email-meta-line">
                <span class="info-label">فرستنده:</span>
                <span id="emailFrom" class="info-val">--</span>
              </div>
              <div class="email-meta-line">
                <span class="info-label">موضوع:</span>
                <span id="emailSubject" class="info-val">--</span>
              </div>
            </div>
            <div id="emailBodyText" class="email-body-text"></div>
          </div>
        </div>

        <!-- PANE 4: EVALUATION & SEAT ASSIGNMENT FORM -->
        <div id="modalPane-eval" class="modal-tab-pane">
          <div style="background: var(--color-paper-card); border: 2px solid var(--color-ink); box-shadow: var(--shadow-card); padding: 20px;">
            <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 16px;">✍️ فرم ارزیابی، تعیین وضعیت و تخصیص ظرفیت</h3>
            <form id="evalForm" onsubmit="handleEvalSubmit(event)" style="display: flex; flex-direction: column; gap: 16px;">
              <input type="hidden" id="evalCandidateId">
              <div class="eval-form-grid">
                
                <div class="form-group">
                  <label for="evalSeatAction">تخصیص ظرفیت آزمایشگاه:</label>
                  <select id="evalSeatSelect" class="form-control">
                    <!-- Populated by JS -->
                  </select>
                </div>

                <div class="form-group">
                  <label for="evalPhase">🎯 فاز اولویت‌بندی مصاحبه:</label>
                  <select id="evalPhase" class="form-control" style="font-weight: 800;">
                    <option value="">بدون فاز (تخصیص‌نیافته)</option>
                    <option value="phase1" style="color: #6D28D9; font-weight: 800;">🟣 فاز ۱ (اولویت اول برای دعوت به مصاحبه)</option>
                    <option value="phase2" style="color: #0369A1; font-weight: 800;">🔵 فاز ۲ (اولویت دوم)</option>
                    <option value="phase3" style="color: #B45309; font-weight: 800;">🟠 فاز ۳ (اولویت سوم)</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="evalStatus">وضعیت متقاضی:</label>
                  <select id="evalStatus" class="form-control">
                    <option value="در انتظار مصاحبه">⏳ در انتظار مصاحبه</option>
                    <option value="دعوت به مصاحبه">📞 دعوت به مصاحبه</option>
                    <option value="مصاحبه انجام شد">✔️ مصاحبه انجام شد</option>
                    <option value="پذیرفته‌شده قطعی">🌟 پذیرفته‌شده قطعی در آزمایشگاه</option>
                    <option value="لیست رزرو">📋 قرارگیری در لیست رزرو</option>
                    <option value="رد شده">❌ عدم پذیرش</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="evalScore">نمره ارزیابی مصاحبه (از ۱۰۰):</label>
                  <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="range" id="evalScoreRange" min="0" max="100" class="form-control" style="flex: 1;" oninput="document.getElementById('evalScore').value = this.value">
                    <input type="number" id="evalScore" min="0" max="100" class="form-control" style="width: 80px; font-weight: 800; font-size: 16px;" oninput="document.getElementById('evalScoreRange').value = this.value" placeholder="--">
                  </div>
                </div>

                <div class="form-group">
                  <label for="evalSlot">تاریخ و ساعت مصاحبه (شمسی):</label>
                  <div style="display: flex; gap: 8px;">
                    <input type="text" id="evalSlot" class="form-control" style="flex: 1; font-weight: 700;">
                    <button type="button" class="card-btn primary" onclick="openShamsiPicker(selectedCandidate.id)" style="white-space: nowrap; padding: 6px 14px;">
                      📅 انتخاب از تقویم شمسی
                    </button>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label for="evalNotes">یادداشت‌های محرمانه مصاحبه‌کننده و بازخورد اساتید:</label>
                <textarea id="evalNotes" class="form-control" rows="5" placeholder="نکات مهم، بازخورد تسلط فنی، انگیزه و پشتکار، تناسب با پروژه‌های جاری آزمایشگاه..."></textarea>
              </div>

              <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px;">
                <button type="submit" class="card-btn primary" style="padding: 10px 24px; font-size: 14px;">
                  💾 ذخیره تغییرات و وضعیت
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </div>
  </div>

  
    <!-- MODERN SHAMSI DATE & TIME PICKER MODAL -->
  <div id="shamsiPickerModalOverlay" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="shamsiPickerTitle" onclick="handleShamsiOverlayClick(event)">
    <div class="shamsi-modal-box">
      
      <!-- Header -->
      <div class="shamsi-modal-header">
        <div class="shamsi-header-info">
          <div class="shamsi-header-icon">📅</div>
          <div>
            <h3 id="shamsiPickerTitle" class="shamsi-header-title">تنظیم نوبت و زمان مصاحبه حضوری (تقویم شمسی)</h3>
            <div id="shamsiPickerCandidateSubtitle" class="shamsi-header-subtitle">متقاضی: --</div>
          </div>
        </div>
        <button class="shamsi-close-btn" onclick="closeShamsiPickerModal()" title="بستن">✕</button>
      </div>

      <!-- Body -->
      <div class="shamsi-modal-body">
        <input type="hidden" id="shamsiPickerCid">

        <!-- STEP 1: DATE SELECTION -->
        <div class="shamsi-section">
          <div class="shamsi-section-head">
            <span class="shamsi-step-badge">۱</span>
            <span class="shamsi-section-title">انتخاب روز مصاحبه</span>
            <span class="shamsi-section-desc">روز مورد نظر را از تقویم پیش‌فرض انتخاب کنید:</span>
          </div>

          <!-- Quick Date Chips Grid -->
          <div class="shamsi-chips-grid" id="shamsiDateChipsContainer">
            <!-- Populated dynamically by JS -->
          </div>

          <!-- Custom Date Toggle and Box -->
          <div style="margin-top: 6px;">
            <button type="button" class="shamsi-toggle-custom-btn" onclick="toggleCustomDate()">
              <span id="customDateToggleIcon">⚙️</span>
              <span id="customDateToggleText">انتخاب تاریخ دلخواه دیگر از تقویم شمسی...</span>
            </button>
          </div>

          <div class="shamsi-custom-box" id="shamsiCustomDateBox" style="display: none;">
            <div class="shamsi-inputs-row">
              <div class="shamsi-field">
                <label>روز هفته:</label>
                <select id="shamsiDayOfWeek" class="shamsi-select" onchange="onCustomDateInputChanged()">
                  <option value="شنبه">شنبه</option>
                  <option value="یکشنبه">یکشنبه</option>
                  <option value="دوشنبه">دوشنبه</option>
                  <option value="سه‌شنبه">سه‌شنبه</option>
                  <option value="چهارشنبه">چهارشنبه</option>
                  <option value="پنج‌شنبه">پنج‌شنبه</option>
                </select>
              </div>
              <div class="shamsi-field">
                <label>روز ماه:</label>
                <select id="shamsiDayOfMonth" class="shamsi-select" onchange="onCustomDateInputChanged()">
                  <!-- 1 to 31 -->
                </select>
              </div>
              <div class="shamsi-field">
                <label>ماه:</label>
                <select id="shamsiMonth" class="shamsi-select" onchange="onCustomDateInputChanged()">
                  <option value="مهر">مهر</option>
                  <option value="آبان" selected>آبان</option>
                  <option value="آذر">آذر</option>
                  <option value="دی">دی</option>
                  <option value="بهمن">بهمن</option>
                  <option value="اسفند">اسفند</option>
                </select>
              </div>
              <div class="shamsi-field">
                <label>سال:</label>
                <input type="text" id="shamsiYear" class="shamsi-input" value="۱۴۰۵" readonly>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 2: TIME SELECTION -->
        <div class="shamsi-section">
          <div class="shamsi-section-head">
            <span class="shamsi-step-badge">۲</span>
            <span class="shamsi-section-title">انتخاب بازه زمانی جلسه مصاحبه</span>
            <span class="shamsi-section-desc">اسلات‌های استاندارد ۲۰ دقیقه‌ای مصاحبه:</span>
          </div>

          <!-- Morning Slots -->
          <div class="shamsi-time-category">
            <span class="shamsi-time-label">☀️ نوبت صبح:</span>
            <div class="shamsi-time-chips" id="shamsiMorningChipsContainer">
              <!-- Morning chips -->
            </div>
          </div>

          <!-- Afternoon Slots -->
          <div class="shamsi-time-category" style="margin-top: 8px;">
            <span class="shamsi-time-label">🌤️ نوبت عصر:</span>
            <div class="shamsi-time-chips" id="shamsiAfternoonChipsContainer">
              <!-- Afternoon chips -->
            </div>
          </div>

          <!-- Custom Time Details Toggle and Box -->
          <div style="margin-top: 6px;">
            <button type="button" class="shamsi-toggle-custom-btn" onclick="toggleCustomTime()">
              <span id="customTimeToggleIcon">⏱️</span>
              <span id="customTimeToggleText">تعیین ساعت، دقیقه و مدت مصاحبه به دلخواه...</span>
            </button>
          </div>

          <div class="shamsi-custom-box" id="shamsiCustomTimeBox" style="display: none;">
            <div class="shamsi-inputs-row">
              <div class="shamsi-field">
                <label>ساعت شروع:</label>
                <select id="shamsiStartHour" class="shamsi-select" onchange="onCustomTimeInputChanged()">
                  <!-- 08 to 20 -->
                </select>
              </div>
              <div class="shamsi-field">
                <label>دقیقه شروع:</label>
                <select id="shamsiStartMin" class="shamsi-select" onchange="onCustomTimeInputChanged()">
                  <option value="00">۰۰</option>
                  <option value="05">۰۵</option>
                  <option value="10">۱۰</option>
                  <option value="15">۱۵</option>
                  <option value="20">۲۰</option>
                  <option value="25">۲۵</option>
                  <option value="30">۳۰</option>
                  <option value="35">۳۵</option>
                  <option value="40">۴۰</option>
                  <option value="45">۴۵</option>
                  <option value="50">۵۰</option>
                  <option value="55">۵۵</option>
                </select>
              </div>
              <div class="shamsi-field">
                <label>مدت مصاحبه:</label>
                <select id="shamsiDuration" class="shamsi-select" onchange="onCustomTimeInputChanged()">
                  <option value="15">۱۵ دقیقه</option>
                  <option value="20" selected>۲۰ دقیقه</option>
                  <option value="25">۲۵ دقیقه</option>
                  <option value="30">۳۰ دقیقه</option>
                  <option value="45">۴۵ دقیقه</option>
                  <option value="60">۱ ساعت</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 3: LIVE SUMMARY CONFIRMATION CARD -->
        <div class="shamsi-summary-card">
          <div class="shamsi-summary-top">
            <span class="shamsi-summary-tag">خلاصه زمان‌بندی جلسه مصاحبه</span>
            <span class="shamsi-loc-tag">📍 __LOCATION_DEFAULT__</span>
          </div>
          <div class="shamsi-summary-content">
            <div class="shamsi-summary-icon">🗓️</div>
            <div class="shamsi-summary-text">
              <div id="shamsiFinalPreviewDate" class="shamsi-final-date">سه‌شنبه ۱۹ آبان ۱۴۰۵</div>
              <div id="shamsiFinalPreviewTime" class="shamsi-final-time">ساعت ۰۹:۱۰ تا ۰۹:۳۰ (۲۰ دقیقه - حضوری)</div>
            </div>
          </div>

          <!-- Direct text override option -->
          <div class="shamsi-manual-override-box">
            <a href="javascript:void(0)" class="shamsi-manual-link" onclick="toggleManualInput()">
              ✏️ ویرایش دستی متن نهایی نوبت (در صورت نیاز به ثبت توضیحات ویژه)
            </a>
            <div id="shamsiManualContainer" style="display: none; margin-top: 6px;">
              <input type="text" id="shamsiManualSlotInput" class="shamsi-input-manual" placeholder="مثال: سه‌شنبه ۱۹ آبان ۱۴۰۵ · ۰۹:۱۰ تا ۰۹:۳۰">
            </div>
          </div>
        </div>

      </div>

      <!-- Footer Buttons -->
      <div class="shamsi-modal-footer">
        <button type="button" class="shamsi-btn-cancel" onclick="closeShamsiPickerModal()">
          انصراف
        </button>
        <button type="button" class="shamsi-btn-submit" onclick="saveShamsiTimePicker()">
          ✔️ تأیید و ثبت زمان مصاحبه
        </button>
      </div>

    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  
  <!-- EMAIL TEMPLATE GENERATOR MODAL -->
  <div id="emailTemplateModalOverlay" class="modal-overlay" role="dialog" aria-modal="true" aria-label="قالب‌ساز خودکار ایمیل و مکاتبه با متقاضی" onclick="handleEmailModalOverlayClick(event)">
    <div class="modal-window" style="max-width: 820px; max-height: 92vh; background: var(--color-paper-card); border: 3px solid var(--color-ink); box-shadow: var(--shadow-card-hover); border-radius: 6px; overflow: hidden; display: flex; flex-direction: column;">
      <div class="modal-header" style="background: var(--color-ink); color: var(--color-paper); border-bottom: 3px solid var(--color-ai); padding: 14px 20px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 26px;">✉️</span>
          <div>
            <h2 style="font-size: 17px; font-weight: 900; margin-bottom: 2px;">قالب‌ساز خودکار ایمیل و مکاتبه با متقاضی</h2>
            <p id="emailModalCandidateSubtitle" style="font-size: 12px; opacity: 0.85; color: var(--color-ai-light);">متقاضی: --</p>
          </div>
        </div>
        <button class="modal-close-btn" style="color: #fff;" onclick="closeEmailModal()">✕</button>
      </div>

      <div class="modal-body" style="padding: 20px; overflow-y: auto;">
        <!-- TEMPLATE TYPE SELECTOR BUTTONS -->
        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 12px; font-weight: 800; color: var(--color-ink-muted); margin-bottom: 8px;">
            🎯 انتخاب نوع قالب پیام (جهت بارگذاری خودکار متن و متغیرها):
          </label>
          <div class="email-templates-grid">
            <button type="button" class="email-tpl-btn active" onclick="selectEmailTemplate('interview', this)">
              <span class="tpl-icon">📅</span>
              <div class="tpl-info">
                <b>دعوت به مصاحبه حضوری</b>
                <small>ساعت، تاریخ و لوکیشن مصاحبه</small>
              </div>
            </button>
            <button type="button" class="email-tpl-btn" onclick="selectEmailTemplate('simple_interview', this)">
              <span class="tpl-icon">📍</span>
              <div class="tpl-info">
                <b>دعوت ساده / لوکیشن جایگزین</b>
                <small>متن کوتاه + لوکیشن نشان</small>
              </div>
            </button>
            <button type="button" class="email-tpl-btn" onclick="selectEmailTemplate('accepted', this)">
              <span class="tpl-icon">🌟</span>
              <div class="tpl-info">
                <b>اعلام قبولی قطعی</b>
                <small>تبریک و تخصیص ظرفیت</small>
              </div>
            </button>
            <button type="button" class="email-tpl-btn" onclick="selectEmailTemplate('waitlist', this)">
              <span class="tpl-icon">⏳</span>
              <div class="tpl-info">
                <b>لیست انتظار (رزرو)</b>
                <small>اطلاع‌رسانی اولویت رزرو</small>
              </div>
            </button>
            <button type="button" class="email-tpl-btn" onclick="selectEmailTemplate('rejected', this)">
              <span class="tpl-icon">❌</span>
              <div class="tpl-info">
                <b>عدم پذیرش محترمانه</b>
                <small>تشکر و آرزوی موفقیت</small>
              </div>
            </button>
            <button type="button" class="email-tpl-btn" onclick="selectEmailTemplate('docs', this)">
              <span class="tpl-icon">📄</span>
              <div class="tpl-info">
                <b>درخواست مدارک تکمیلی</b>
                <small>کارنامه، گیت‌هاب و مقالات</small>
              </div>
            </button>
          </div>
        </div>

        <!-- RECIPIENT & SUBJECT ROW -->
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 14px;">
          <div>
            <label style="display: block; font-size: 11.5px; font-weight: 800; margin-bottom: 4px;">آدرس ایمیل گیرنده:</label>
            <div style="position: relative;">
              <input type="text" id="emailModalTo" class="form-control" style="direction: ltr; text-align: left; font-size: 12.5px; background: #fff;" readonly>
            </div>
          </div>
          <div>
            <label style="display: block; font-size: 11.5px; font-weight: 800; margin-bottom: 4px;">موضوع ایمیل:</label>
            <div style="display: flex; gap: 6px;">
              <input type="text" id="emailModalSubject" class="form-control" style="font-weight: 700; font-size: 12px; background: #fff;">
              <button type="button" class="card-btn" style="white-space: nowrap; font-size: 11px;" onclick="copyEmailSubject()">
                📋 کپی موضوع
              </button>
            </div>
          </div>
        </div>

        <!-- EMAIL BODY TEXTAREA -->
        <div style="margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label style="font-size: 12px; font-weight: 800;">متن ایمیل (قابل ویرایش پیش از ارسال):</label>
            <span style="font-size: 11px; color: var(--color-ink-muted);">متغیرها (نام، تاریخ و ساعت، گرایش و نام استاد) پر شده‌اند.</span>
          </div>
          <textarea id="emailModalBody" class="form-control" rows="12" style="font-family: inherit; font-size: 12.5px; line-height: 1.8; padding: 12px; border: 2px solid var(--color-ink); background: #FAF7EE; white-space: pre-wrap;"></textarea>
        </div>

        <!-- FOOTER ACTIONS -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-top: 2px solid var(--color-border); padding-top: 14px;">
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button type="button" class="card-btn primary" style="padding: 8px 16px; font-size: 12.5px; font-weight: 800; display: flex; align-items: center; gap: 6px;" onclick="copyEmailBody()">
              <span>📋</span>
              <span>کپی متن پیام</span>
            </button>
            <button type="button" class="card-btn" style="padding: 8px 14px; font-size: 12.5px; font-weight: 700; display: flex; align-items: center; gap: 6px; background: #2563EB; color: #fff; border-color: #1D4ED8;" onclick="openMailto()">
              <span>📧</span>
              <span>ارسال مستقیم با نرم‌افزار ایمیل</span>
            </button>
            <button type="button" class="card-btn" style="padding: 8px 14px; font-size: 12.5px; font-weight: 700; display: flex; align-items: center; gap: 6px; background: #EA4335; color: #fff; border-color: #C5221F;" onclick="openGmailWeb()">
              <span>🌐</span>
              <span>ارسال سریع با Gmail Web</span>
            </button>
          </div>
          <button type="button" class="card-btn" style="padding: 8px 16px; font-size: 12.5px;" onclick="closeEmailModal()">بستن</button>
        </div>
      </div>
    </div>
  </div>

  <!-- SEAT PICKER MODAL OVERLAY -->
  <div id="seatPickerModalOverlay" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="seatPickerModalTitle" onclick="handleSeatPickerOverlayClick(event)">
    <div class="modal-window" style="max-width: 680px; width: 94%; max-height: 88vh; background: #FFFFFF; border: 3px solid var(--color-ink); box-shadow: var(--shadow-card-hover); border-radius: 8px; display: flex; flex-direction: column; overflow: hidden;">
      
      <!-- HEADER -->
      <div style="background: var(--color-paper-alt); border-bottom: 2px solid var(--color-ink); padding: 12px 18px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3 id="seatPickerModalTitle" style="margin: 0; font-size: 16px; font-weight: 900; color: var(--color-ink);">🏛️ تخصیص متقاضی به ظرفیت</h3>
          <div id="seatPickerModalSubtitle" style="font-size: 11.5px; color: var(--color-ink-muted); margin-top: 3px;"></div>
        </div>
        <button type="button" class="card-btn" onclick="closeSeatPickerModal()" style="font-size: 14px; font-weight: 900; padding: 2px 8px;">✕</button>
      </div>

      <!-- SEARCH & FILTER BAR -->
      <div style="padding: 10px 16px; background: #F8FAFC; border-bottom: 1.5px solid #E2E8F0; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
        <div class="search-box" style="flex: 1; min-width: 200px;">
          <span class="search-icon">🔍</span>
          <input type="text" id="seatPickerSearchInput" class="search-input" placeholder="جستجو در نام متقاضی، دانشگاه، رتبه..." oninput="filterSeatPickerList()">
        </div>
        <div id="seatPickerFilterChips" style="display: flex; gap: 4px;"></div>
      </div>

      <!-- CANDIDATES LIST -->
      <div id="seatPickerCandidatesList" style="padding: 12px 16px; overflow-y: auto; max-height: 55vh; display: flex; flex-direction: column; gap: 8px;">
        <!-- Populated dynamically -->
      </div>

      <!-- FOOTER -->
      <div style="background: var(--color-paper-alt); border-top: 1.5px solid var(--color-ink); padding: 10px 18px; display: flex; justify-content: space-between; align-items: center;">
        <span id="seatPickerCandidateCount" style="font-size: 12px; font-weight: 700; color: var(--color-ink-muted);"></span>
        <button type="button" class="card-btn" onclick="closeSeatPickerModal()" style="font-size: 12px; padding: 4px 14px;">بستن پنجره</button>
      </div>
    </div>
  </div>

  <div id="toastMsg" class="toast-msg">
    <span>✔️</span>
    <span id="toastText">عملیات با موفقیت انجام شد</span>
  </div>

  <!-- PAGE FOOTER -->
  <footer class="page-footer">
    <div>
      <b>دانشگاه علم و صنعت ایران</b> · دانشکده مهندسی کامپیوتر · <b>آزمایشگاه داده‌کاوی (DML)</b>
    </div>
    <div>
      استاد راهنما: <b>دکتر بهروز مینایی بیدگلی</b> | پذیرش کارشناسی ارشد ورودی ۱۴۰۵
    </div>
  </footer>

  <!-- JAVASCRIPT APPLICATION LOGIC -->
  <script>
    const rawCandidates = __RAW_CANDIDATES_JSON__;
    const CONFIG = __CONFIG_JSON__;

    // Seats Configuration loaded from config.json (or fallback)
    const SEATS_CONFIG = (CONFIG.seats && CONFIG.seats.length) ? CONFIG.seats : [
      { id: 'ai_roz_1', group: 'ai_roz', category: 'روزانه هوش مصنوعی', title: '۱. روزانه هوش', track: 'AI', quota: 'روزانه' },
      { id: 'ai_roz_2', group: 'ai_roz', category: 'روزانه هوش مصنوعی', title: '۲. روزانه هوش', track: 'AI', quota: 'روزانه' },
      { id: 'ai_shab_1', group: 'ai_shab', category: 'شبانه هوش مصنوعی', title: '۳. شبانه هوش', track: 'AI', quota: 'شبانه' },
      { id: 'ai_shab_2', group: 'ai_shab', category: 'شبانه هوش مصنوعی', title: '۴. شبانه هوش', track: 'AI', quota: 'شبانه' },
      { id: 'sw_roz_1', group: 'sw_roz', category: 'روزانه نرم‌افزار', title: '۵. روزانه نرم‌افزار', track: 'Software', quota: 'روزانه' },
      { id: 'sw_roz_2', group: 'sw_roz', category: 'روزانه نرم‌افزار', title: '۶. روزانه نرم‌افزار', track: 'Software', quota: 'روزانه' },
      { id: 'sw_roz_3', group: 'sw_roz', category: 'روزانه نرم‌افزار', title: '۷. روزانه نرم‌افزار', track: 'Software', quota: 'روزانه' },
      { id: 'sw_roz_4', group: 'sw_roz', category: 'روزانه نرم‌افزار', title: '۸. روزانه نرم‌افزار', track: 'Software', quota: 'روزانه' }
    ];

    let candidates = [];
    let seatsState = {}; // mapping: seat_id -> candidate_id (or null)
    let currentFilter = 'all';
    let currentPhaseFilter = 'all';
    let currentFilesTrackFilter = 'all';
    let currentSort = 'priority';
    let currentViewMode = 'cards';
    let starredIds = new Set();
    let selectedCandidate = null;

    // Helper functions for candidate classification
    function isCandidateShabaneh(cand) {
      if (!cand) return false;
      const adm = cand.admission_type || '';
      const quo = cand.quota || '';
      return adm.includes('شبانه') || quo.includes('شبانه');
    }

    function isCandidateTalented(cand) {
      if (!cand) return false;
      const adm = cand.admission_type || '';
      const quo = cand.quota || '';
      return adm.includes('استعداد') || quo.includes('استعداد');
    }

    function isCandidateAI(cand) {
      if (!cand) return false;
      return cand.track_en === 'AI' || (cand.track && cand.track.includes('هوش'));
    }

    function isCandidateSoftware(cand) {
      if (!cand) return false;
      return cand.track_en === 'Software' || (cand.track && cand.track.includes('نرم‌افزار'));
    }

    // Default Track-Based Comparator: AI candidates grouped first, Software candidates grouped second
    function defaultCandidateSort(a, b) {
      // 1. Primary: Track (AI first, Software second)
      const isAI_a = isCandidateAI(a) ? 1 : 2;
      const isAI_b = isCandidateAI(b) ? 1 : 2;
      if (isAI_a !== isAI_b) return isAI_a - isAI_b;

      // 2. Secondary within track: Talented (استعداد درخشان) priority
      const isTalA = isCandidateTalented(a) ? 1 : 0;
      const isTalB = isCandidateTalented(b) ? 1 : 0;
      if (isTalA !== isTalB) return isTalB - isTalA;

      // 3. Competitive Konkur Rank (صعودی رتبه کنکور)
      const rankA = (a.rank_val !== undefined && a.rank_val !== null) ? a.rank_val : 9999;
      const rankB = (b.rank_val !== undefined && b.rank_val !== null) ? b.rank_val : 9999;
      if (rankA !== rankB) return rankA - rankB;

      // 4. GPA (نزولی معدل)
      const gpaA = a.gpa_val || 0;
      const gpaB = b.gpa_val || 0;
      if (gpaA !== gpaB) return gpaB - gpaA;

      // 5. Fallback: ID
      return a.id - b.id;
    }

    // Format clean, concise labels for dropdown options (prevents BiDi flipping & overflow)
    function formatCandidateOption(c) {
      const isTal = isCandidateTalented(c);
      const isShab = isCandidateShabaneh(c);
      const typeLabel = isTal ? 'استعداد' : (isShab ? 'شبانه' : 'روزانه');
      
      let gpaVal = '-';
      if (c.bsc_gpa) {
        gpaVal = c.bsc_gpa.toString().replace('/20', '').replace('/4.0', '').trim().split(' ')[0] || '-';
      }

      let rankStr = '';
      if (isTal) {
        rankStr = 'معدل ' + gpaVal;
      } else if (c.rank_val && c.rank_val < 9000) {
        rankStr = 'رتبه ' + c.rank_val;
      } else if (c.konkur_arshad && !c.konkur_arshad.includes('استعداد') && !c.konkur_arshad.includes('بدون')) {
        const clean = c.konkur_arshad.replace(/رتبه\s*/g, '').split('/')[0].split('(')[0].trim();
        rankStr = clean ? 'رتبه ' + clean : ('معدل ' + gpaVal);
      } else {
        rankStr = 'معدل ' + gpaVal;
      }
      
      return `${c.name} (${typeLabel} · ${rankStr})`;
    }

    function initData() {
      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      const savedStars = JSON.parse(localStorage.getItem('admission_starred') || '[]');
      const savedSeats = JSON.parse(localStorage.getItem('admission_seats_allocation') || '{}');
      
      starredIds = new Set(savedStars);

      // Default empty seats
      SEATS_CONFIG.forEach(s => {
        seatsState[s.id] = (savedSeats[s.id] !== undefined) ? savedSeats[s.id] : null;
      });

      candidates = rawCandidates.map(c => {
        const cidStr = String(c.id);
        let candObj = { ...c };
        if (savedEvals[cidStr]) {
          if (c.status === 'رد شده' || c.status === 'عدم پذیرش') {
            candObj = { ...candObj, ...savedEvals[cidStr], status: c.status, eval_notes: c.eval_notes || savedEvals[cidStr].eval_notes };
          } else {
            candObj = { ...candObj, ...savedEvals[cidStr] };
          }
        }
        return candObj;
      });

      // Default sort by track: AI first, Software second
      candidates.sort(defaultCandidateSort);

      updateFilterCounts();
    }

    function saveSeatsState() {
      localStorage.setItem('admission_seats_allocation', JSON.stringify(seatsState));
      // POST to Flask server if available
      fetch('/api/seats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(seatsState)
      }).catch(() => {});
    }

    async function syncWithServer() {
      if (!window.location.protocol.startsWith('http')) return;
      try {
        const [candsRes, seatsRes] = await Promise.all([
          fetch('/api/candidates'),
          fetch('/api/seats')
        ]);
        let changed = false;
        if (candsRes.ok) {
          const serverCands = await candsRes.json();
          const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
          serverCands.forEach(sc => {
            const idx = candidates.findIndex(c => c.id === sc.id);
            if (idx !== -1) {
              candidates[idx] = { ...candidates[idx], ...sc };
            }
            const cidStr = String(sc.id);
            if (!savedEvals[cidStr]) savedEvals[cidStr] = {};
            if (sc.interview_phase !== undefined) savedEvals[cidStr].interview_phase = sc.interview_phase;
            if (sc.status) savedEvals[cidStr].status = sc.status;
            if (sc.eval_notes) savedEvals[cidStr].eval_notes = sc.eval_notes;
            if (sc.score !== undefined && sc.score !== null) savedEvals[cidStr].score = sc.score;
            if (sc.interview_slot) savedEvals[cidStr].interview_slot = sc.interview_slot;
          });
          localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));
          changed = true;
        }
        if (seatsRes.ok) {
          const serverSeats = await seatsRes.json();
          seatsState = { ...seatsState, ...serverSeats };
          localStorage.setItem('admission_seats_allocation', JSON.stringify(seatsState));
          changed = true;
        }
        if (changed) {
          updateFilterCounts();
          renderSeatsBoard();
          renderRoster();
          renderTimetable();
          if (typeof renderAnalytics === 'function') renderAnalytics();
          if (typeof renderExportPreview === 'function') renderExportPreview();
        }
      } catch (err) {
        console.warn('Server sync skipped:', err);
      }
    }


    function getPhaseLabel(phase) {
      if (phase === 'phase1') return '🟣 فاز ۱ (اولویت اول)';
      if (phase === 'phase2') return '🔵 فاز ۲ (اولویت دوم)';
      if (phase === 'phase3') return '🟠 فاز ۳ (اولویت سوم)';
      return 'بدون فاز';
    }

    function getPhaseLabelShort(phase) {
      if (phase === 'phase1') return '🟣 فاز ۱';
      if (phase === 'phase2') return '🔵 فاز ۲';
      if (phase === 'phase3') return '🟠 فاز ۳';
      return 'بدون فاز';
    }

    function setPhaseFilter(phaseVal, btn) {
      currentPhaseFilter = phaseVal;
      document.querySelectorAll('.phase-tab-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderRoster();
    }

    function setCandidatePhase(cid, phaseVal, e) {
      if (e) e.stopPropagation();
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;
      cand.interview_phase = phaseVal || null;

      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
      savedEvals[String(cid)].interview_phase = cand.interview_phase;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_phase: cand.interview_phase })
      }).catch(() => {});

      const label = getPhaseLabel(cand.interview_phase);
      showToast(`🎯 فاز «${cand.name}» به «${label}» تنظیم شد`);
      updateFilterCounts();
      renderRoster();
      renderTimetable();
    }

    function updateFilterCounts() {
      const acceptedCount = Object.values(seatsState).filter(cid => cid !== null).length;
      const acceptedBadge = document.getElementById('filterAcceptedCount');
      if (acceptedBadge) acceptedBadge.textContent = acceptedCount;
      const navBadge = document.getElementById('navSeatsBadge');
      if (navBadge) navBadge.textContent = `${acceptedCount} / ${SEATS_CONFIG.length}`;

      const starredBadge = document.getElementById('filterStarredCount');
      if (starredBadge) starredBadge.textContent = starredIds.size;

      // Dynamic counts for all filter tabs
      const totalCount = candidates.length;
      const aiCount = candidates.filter(c => c.track_en === 'AI').length;
      const swCount = candidates.filter(c => c.track_en === 'Software').length;
      const rozCount = candidates.filter(c => (c.quota && c.quota.includes('روزانه')) || (c.admission_type && c.admission_type.includes('روزانه')) || (c.quota && c.quota.includes('استعداد')) || (c.quota && c.quota.includes('بورس'))).length;
      const shabCount = candidates.filter(c => (c.admission_type && c.admission_type.includes('شبانه')) || (c.quota && c.quota.includes('شبانه'))).length;
      const talCount = candidates.filter(c => (c.admission_type && c.admission_type.includes('استعداد')) || (c.quota && c.quota.includes('استعداد'))).length;

      const rejectedCount = candidates.filter(c => c.status === 'رد شده' || c.status === 'عدم پذیرش').length;
      const invitedCount = candidates.filter(c => c.status === 'دعوت به مصاحبه').length;
      const pendingCount = candidates.filter(c => c.status !== 'رد شده' && c.status !== 'عدم پذیرش' && c.status !== 'دعوت به مصاحبه' && getCandidateAssignedSeat(c.id) === null).length;

      const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
      setVal('filterRejectedCount', rejectedCount);
      setVal('filterInvitedCount', invitedCount);
      setVal('filterPendingCount', pendingCount);
      setVal('filterAllCount', totalCount);
      setVal('filterAiCount', aiCount);
      setVal('filterSwCount', swCount);
      setVal('trackAllCount', totalCount);
      setVal('trackAiCount', aiCount);
      setVal('trackSwCount', swCount);
      setVal('filterRozCount', rozCount);
      setVal('filterShabCount', shabCount);
      setVal('filterTalCount', talCount);

      const phase1Count = candidates.filter(c => c.interview_phase === 'phase1').length;
      const phase2Count = candidates.filter(c => c.interview_phase === 'phase2').length;
      const phase3Count = candidates.filter(c => c.interview_phase === 'phase3').length;
      const noPhaseCount = candidates.filter(c => !c.interview_phase).length;
      setVal('filterPhaseAllCount', totalCount);
      setVal('filterPhase1Count', phase1Count);
      setVal('filterPhase2Count', phase2Count);
      setVal('filterPhase3Count', phase3Count);
      setVal('filterNoPhaseCount', noPhaseCount);

      setVal('navRosterBadge', totalCount);
      setVal('headerTotalCount', totalCount);
    }

    // Real-time Persian Clock
    function updateClock() {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('fa-IR');
      const dateStr = now.toLocaleDateString('fa-IR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
      const el = document.getElementById('liveClock');
      if (el) el.textContent = `${dateStr} · ساعت ${timeStr}`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
      }
    }

    function switchMainTab(tabId, btn) {
      if (tabId === 'board') tabId = 'roster';
      document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
      if (btn) btn.classList.add('active');
      const sec = document.getElementById('tab-' + tabId);
      if (sec) sec.classList.add('active');

      if (tabId === 'roster') {
        renderSeatsBoard();
        renderRoster();
      }
      else if (tabId === 'files') renderFilesExplorer();
      else if (tabId === 'analytics') renderAnalytics();
      else if (tabId === 'export') renderExportStudio();
    }

    function switchModalTab(tabId, btn) {
      document.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.modal-tab-pane').forEach(p => p.classList.remove('active'));
      if (btn) btn.classList.add('active');
      const pane = document.getElementById('modalPane-' + tabId);
      if (pane) pane.classList.add('active');
    }

    // ==========================================
    // COMPACT SEATS RENDERING & LOGIC
    // ==========================================
    function renderSeatsBoard() {
      const aiContainer = document.getElementById('aiSeatsGrid');
      const swContainer = document.getElementById('swSeatsGrid');
      const fallbackContainer = document.getElementById('compactSeatsGrid');

      if (aiContainer) aiContainer.innerHTML = '';
      if (swContainer) swContainer.innerHTML = '';
      if (fallbackContainer && !aiContainer) fallbackContainer.innerHTML = '';

      SEATS_CONFIG.forEach(seat => {
        const assignedCid = seatsState[seat.id];
        const cand = assignedCid ? candidates.find(c => c.id === assignedCid) : null;

        let trackClass = 'ai';
        if (seat.track === 'Software') {
          trackClass = isCandidateTalented(cand) ? 'talented' : 'sw';
        } else {
          if (isCandidateTalented(cand)) {
            trackClass = 'talented';
          } else if (seat.group === 'ai_shab' || isCandidateShabaneh(cand)) {
            trackClass = 'shab';
          } else {
            trackClass = 'ai';
          }
        }

        const card = document.createElement('div');
        card.className = `compact-seat-card ${cand ? 'occupied ' + trackClass : seat.group}`;

        if (!cand) {
          let eligibleCandidates = [];
          if (seat.group === 'ai_shab') {
            // هوش شبانه: فقط متقاضیان گرایش هوش شبانه
            eligibleCandidates = candidates.filter(c => isCandidateAI(c) && isCandidateShabaneh(c));
          } else if (seat.group === 'ai_roz') {
            // هوش روزانه: متقاضیان هوش روزانه و استعداد درخشان (غیر شبانه)
            eligibleCandidates = candidates.filter(c => isCandidateAI(c) && !isCandidateShabaneh(c));
          } else if (seat.group === 'sw_roz') {
            // نرم‌افزار روزانه: متقاضیان نرم‌افزار روزانه و استعداد درخشان (غیر شبانه)
            eligibleCandidates = candidates.filter(c => isCandidateSoftware(c) && !isCandidateShabaneh(c));
          } else {
            eligibleCandidates = candidates.filter(c => seat.track === 'Software' ? isCandidateSoftware(c) : isCandidateAI(c));
          }

          eligibleCandidates.sort((a, b) => {
            const aAssigned = isCandidateAssigned(a.id) ? 1 : 0;
            const bAssigned = isCandidateAssigned(b.id) ? 1 : 0;
            if (aAssigned !== bAssigned) return aAssigned - bAssigned;
            return (a.rank_val || 9999) - (b.rank_val || 9999);
          });

          card.innerHTML = `
            <div class="compact-seat-header">
              <span class="compact-seat-title">${seat.title}</span>
              <span class="compact-seat-tag">خالی</span>
            </div>
            <div class="compact-seat-body">
              <button type="button" class="btn-seat-choose" onclick="openSeatPickerModal('${seat.id}')" title="مشاهده لیست کامل متقاضیان و انتخاب برای «${seat.title}»">
                <span>➕ انتخاب متقاضی...</span>
                <span class="btn-seat-count-tag">${eligibleCandidates.length} واجد شرایط</span>
              </button>
            </div>
          `;
        } else {
          card.innerHTML = `
            <div class="compact-seat-header">
              <span class="compact-seat-title" style="font-weight: 900;">${seat.title}</span>
              <button class="compact-seat-vacate" onclick="vacateSeat('${seat.id}')" title="لغو قبولی و تخلیه ظرفیت">✕ تخلیه</button>
            </div>
            <div class="compact-seat-body occupied" onclick="openDossierModal(${cand.id})" title="مشاهده پرونده ${cand.name}">
              <div class="compact-seat-avatar" style="background: ${cand.color};">${cand.initials}</div>
              <div class="compact-seat-info">
                <div class="compact-seat-name">${cand.name}</div>
                <div class="compact-seat-meta">
                  <span>${cand.admission_type?.includes('استعداد') ? 'استعداد درخشان' : (cand.admission_type?.includes('شبانه') ? 'نوبت دوم' : 'روزانه')}</span>
                  <span>·</span>
                  <span>معدل ${cand.bsc_gpa || '-'}</span>
                </div>
              </div>
            </div>
          `;
        }

        if (seat.track === 'AI' && aiContainer) {
          aiContainer.appendChild(card);
        } else if (seat.track === 'Software' && swContainer) {
          swContainer.appendChild(card);
        } else if (fallbackContainer) {
          fallbackContainer.appendChild(card);
        }
      });

      updateKpis();
    }

    function updateKpis() {
      const countGroup = (groupKey) => SEATS_CONFIG.filter(s => s.group === groupKey && seatsState[s.id] !== null).length;
      
      const swRozCount = countGroup('sw_roz');
      const aiRozCount = countGroup('ai_roz');
      const aiShabCount = countGroup('ai_shab');

      const setKpi = (idVal, count, max) => {
        const elVal = document.getElementById(idVal);
        if (elVal) elVal.textContent = `${count} از ${max}`;
      };

      setKpi('kpiSwRoz', swRozCount, 4);
      setKpi('kpiAiRoz', aiRozCount, 2);
      setKpi('kpiAiShab', aiShabCount, 2);

      updateFilterCounts();
    }

    // Check which seat a candidate is on (if any)
    function getCandidateAssignedSeat(cid) {
      for (const [seatId, assignedCid] of Object.entries(seatsState)) {
        if (assignedCid === cid) {
          return SEATS_CONFIG.find(s => s.id === seatId);
        }
      }
      return null;
    }

    function isCandidateAssigned(cid) {
      return getCandidateAssignedSeat(cid) !== null;
    }

    // Direct Assign Candidate from Dropdown
    function handleDirectSeatSelect(seatId, cidStr) {
      if (!cidStr) return;
      const cid = parseInt(cidStr);
      assignCandidateToSeat(cid, seatId);
    }

    // ==========================================
    // SEAT PICKER MODAL (Interactive Candidate Selector)
    // ==========================================
    let currentPickerSeatId = null;
    let currentPickerFilter = 'eligible'; // 'eligible' | 'unassigned' | 'all'

    function handleSeatPickerOverlayClick(e) {
      if (e.target && e.target.id === 'seatPickerModalOverlay') {
        closeSeatPickerModal();
      }
    }

    function openSeatPickerModal(seatId) {
      const seat = SEATS_CONFIG.find(s => s.id === seatId);
      if (!seat) return;
      currentPickerSeatId = seatId;
      currentPickerFilter = 'eligible';

      const titleEl = document.getElementById('seatPickerModalTitle');
      const subEl = document.getElementById('seatPickerModalSubtitle');
      const searchInput = document.getElementById('seatPickerSearchInput');

      if (titleEl) titleEl.textContent = `🏛️ تخصیص متقاضی به «${seat.title}»`;

      let quotaDesc = '';
      if (seat.group === 'sw_roz') {
        quotaDesc = 'سهمیه نرم‌افزار روزانه (متقاضیان گرایش نرم‌افزار روزانه و استعداد درخشان)';
      } else if (seat.group === 'ai_roz') {
        quotaDesc = 'سهمیه هوش مصنوعی روزانه (متقاضیان گرایش هوش مصنوعی روزانه و استعداد درخشان)';
      } else if (seat.group === 'ai_shab') {
        quotaDesc = 'سهمیه هوش مصنوعی نوبت دوم (فقط متقاضیان پذیرفته‌شده نوبت دوم/شبانه هوش مصنوعی)';
      }
      if (subEl) subEl.textContent = quotaDesc;
      if (searchInput) searchInput.value = '';

      renderSeatPickerChips();
      renderSeatPickerList();

      const overlay = document.getElementById('seatPickerModalOverlay');
      if (overlay) overlay.classList.add('active');
      setTimeout(() => { if (searchInput) searchInput.focus(); }, 60);
    }

    function closeSeatPickerModal() {
      const overlay = document.getElementById('seatPickerModalOverlay');
      if (overlay) overlay.classList.remove('active');
      currentPickerSeatId = null;
    }

    function renderSeatPickerChips() {
      const chipsEl = document.getElementById('seatPickerFilterChips');
      if (!chipsEl) return;

      const filters = [
        { key: 'eligible', label: '🎯 واجد شرایط این صندلی' },
        { key: 'unassigned', label: '⏳ بدون صندلی' },
        { key: 'all', label: '👥 کل متقاضیان' }
      ];

      chipsEl.innerHTML = filters.map(f => `
        <button type="button" class="filter-chip ${currentPickerFilter === f.key ? 'active' : ''}" 
          style="font-size: 11px; padding: 4px 10px; border-radius: 4px; border: 1.5px solid ${currentPickerFilter === f.key ? 'var(--color-ink)' : '#CBD5E1'}; background: ${currentPickerFilter === f.key ? 'var(--color-ink)' : '#FFFFFF'}; color: ${currentPickerFilter === f.key ? '#FFFFFF' : 'var(--color-ink)'}; cursor: pointer; font-weight: 800; font-family: inherit;"
          onclick="setPickerFilter('${f.key}')">
          ${f.label}
        </button>
      `).join('');
    }

    function setPickerFilter(filterKey) {
      currentPickerFilter = filterKey;
      renderSeatPickerChips();
      renderSeatPickerList();
    }

    function filterSeatPickerList() {
      renderSeatPickerList();
    }

    function renderSeatPickerList() {
      const listEl = document.getElementById('seatPickerCandidatesList');
      const countEl = document.getElementById('seatPickerCandidateCount');
      const searchInput = document.getElementById('seatPickerSearchInput');
      if (!listEl || !currentPickerSeatId) return;

      const seat = SEATS_CONFIG.find(s => s.id === currentPickerSeatId);
      if (!seat) return;

      const query = (searchInput ? searchInput.value : '').trim().toLowerCase();

      // Base candidate set
      let pool = candidates.slice();

      // Filter by selection mode
      if (currentPickerFilter === 'eligible') {
        if (seat.group === 'ai_shab') {
          pool = pool.filter(c => isCandidateAI(c) && isCandidateShabaneh(c));
        } else if (seat.group === 'ai_roz') {
          pool = pool.filter(c => isCandidateAI(c) && !isCandidateShabaneh(c));
        } else if (seat.group === 'sw_roz') {
          pool = pool.filter(c => isCandidateSoftware(c) && !isCandidateShabaneh(c));
        }
      } else if (currentPickerFilter === 'unassigned') {
        pool = pool.filter(c => !isCandidateAssigned(c.id));
      }

      // Search query filter
      if (query) {
        pool = pool.filter(c => {
          const matchName = (c.name || '').toLowerCase().includes(query);
          const matchUni = (c.bsc_uni || '').toLowerCase().includes(query);
          const matchRank = (c.konkur_arshad || '').toLowerCase().includes(query);
          const matchAdmission = (c.admission_type || '').toLowerCase().includes(query);
          const matchTrack = (c.track || '').toLowerCase().includes(query);
          return matchName || matchUni || matchRank || matchAdmission || matchTrack;
        });
      }

      // Sort: candidate currently in this seat first, then unassigned, then by rank/GPA
      pool.sort((a, b) => {
        const aThisSeat = seatsState[seat.id] === a.id ? -2 : 0;
        const bThisSeat = seatsState[seat.id] === b.id ? -2 : 0;
        if (aThisSeat !== bThisSeat) return aThisSeat - bThisSeat;

        const aAssigned = isCandidateAssigned(a.id) ? 1 : 0;
        const bAssigned = isCandidateAssigned(b.id) ? 1 : 0;
        if (aAssigned !== bAssigned) return aAssigned - bAssigned;

        return (a.rank_val || 9999) - (b.rank_val || 9999);
      });

      if (countEl) {
        countEl.textContent = `نمایش ${pool.length} متقاضی`;
      }

      if (pool.length === 0) {
        listEl.innerHTML = `
          <div style="text-align: center; padding: 24px; color: var(--color-ink-muted); font-size: 13px;">
            موردی مطابق با شرایط و جستجوی شما یافت نشد.
          </div>
        `;
        return;
      }

      listEl.innerHTML = pool.map(c => {
        const assignedSeat = getCandidateAssignedSeat(c.id);
        const isAssignedHere = assignedSeat && assignedSeat.id === seat.id;
        const isAssignedElsewhere = assignedSeat && assignedSeat.id !== seat.id;
        const isTal = isCandidateTalented(c);
        const isShab = isCandidateShabaneh(c);
        const typeLabel = isTal ? 'استعداد درخشان' : (isShab ? 'نوبت دوم (شبانه)' : 'روزانه');
        const typeBg = isTal ? '#EDE9FE' : (isShab ? '#FEF3C7' : '#DCFCE7');
        const typeColor = isTal ? '#5B21B6' : (isShab ? '#92400E' : '#166534');

        let rankPart = '';
        if (isTal) {
          rankPart = `معدل: ${c.bsc_gpa || '-'}`;
        } else if (c.rank_val && c.rank_val < 9000) {
          rankPart = `رتبه کنکور: ${c.rank_val} · معدل: ${c.bsc_gpa || '-'}`;
        } else if (c.konkur_arshad) {
          rankPart = `${c.konkur_arshad} · معدل: ${c.bsc_gpa || '-'}`;
        } else {
          rankPart = `معدل: ${c.bsc_gpa || '-'}`;
        }

        let actionButtonHtml = '';
        if (isAssignedHere) {
          actionButtonHtml = `
            <div style="display: flex; gap: 4px; align-items: center;">
              <span style="font-size: 11px; font-weight: 800; color: #15803D; background: #DCFCE7; padding: 4px 8px; border-radius: 4px; border: 1px solid #86EFAC;">
                ✓ قبولی در همین صندلی
              </span>
              <button type="button" class="card-btn" style="padding: 4px 8px; font-size: 11px; color: #DC2626;" onclick="vacateSeat('${seat.id}');">
                ✕ تخلیه
              </button>
            </div>
          `;
        } else if (isAssignedElsewhere) {
          actionButtonHtml = `
            <button type="button" class="card-btn" style="padding: 5px 10px; font-size: 11.5px; font-weight: 800; background: #FFFBEB; border-color: #F59E0B; color: #B45309;" 
              onclick="assignCandidateToSeat(${c.id}, '${seat.id}'); closeSeatPickerModal();" 
              title="انتقال از «${assignedSeat.title}» به «${seat.title}»">
              ⇄ انتقال به این صندلی (از ${assignedSeat.title})
            </button>
          `;
        } else {
          actionButtonHtml = `
            <button type="button" class="card-btn primary" style="padding: 5px 12px; font-size: 12px; font-weight: 800;" 
              onclick="assignCandidateToSeat(${c.id}, '${seat.id}'); closeSeatPickerModal();">
              ➕ تخصیص به این صندلی
            </button>
          `;
        }

        return `
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 8px 12px; background: #FFFFFF; border: 1.5px solid ${isAssignedHere ? '#10B981' : '#E2E8F0'}; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">
              <div style="width: 32px; height: 32px; border-radius: 50%; background: ${c.color}; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; flex-shrink: 0;">
                ${c.initials}
              </div>
              <div style="min-width: 0;">
                <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                  <span style="font-weight: 900; font-size: 13px; color: var(--color-ink); cursor: pointer;" onclick="openDossierModal(${c.id})">${c.name}</span>
                  <span style="font-size: 10px; font-weight: 800; padding: 1px 6px; border-radius: 3px; background: ${typeBg}; color: ${typeColor};">${typeLabel}</span>
                  <span style="font-size: 10px; color: var(--color-ink-muted);">گرایش ${c.track || '-'}</span>
                </div>
                <div style="font-size: 11px; color: var(--color-ink-muted); margin-top: 2px;">
                  <span>دانشگاه ${c.bsc_uni || '-'}</span> · <span>${rankPart}</span>
                </div>
              </div>
            </div>
            <div style="flex-shrink: 0;">
              ${actionButtonHtml}
            </div>
          </div>
        `;
      }).join('');
    }

    // Smart Auto-Assign on "قبول" Button Click
    function toggleCandidateAcceptance(cid) {
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;

      const currentSeat = getCandidateAssignedSeat(cid);
      if (currentSeat) {
        vacateSeat(currentSeat.id);
        return;
      }

      const isCandSw = isCandidateSoftware(cand);
      let targetSeat = null;

      if (isCandSw) {
        // Software applicants: all software seats are sw_roz (1, 2, 3)
        targetSeat = SEATS_CONFIG.find(s => s.group === 'sw_roz' && seatsState[s.id] === null);
      } else {
        // AI applicants:
        if (isCandidateShabaneh(cand)) {
          targetSeat = SEATS_CONFIG.find(s => s.group === 'ai_shab' && seatsState[s.id] === null);
        } else {
          // Rozaneh or Talented AI applicants
          targetSeat = SEATS_CONFIG.find(s => s.group === 'ai_roz' && seatsState[s.id] === null);
        }
      }

      if (!targetSeat) {
        const quotaName = isCandSw ? 'نرم‌افزار روزانه' : (isCandidateShabaneh(cand) ? 'هوش مصنوعی نوبت دوم (شبانه)' : 'هوش مصنوعی روزانه');
        alert(`⚠️ تمامی ظرفیت‌های مصوب مربوط به بخش «${quotaName}» پر شده‌اند! لطفاً ابتدا یکی از صندلی‌های این بخش را خالی کنید.`);
        return;
      }

      assignCandidateToSeat(cid, targetSeat.id);
    }
        function toggleCandidateInvitation(cid) {
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;

      const isCurrentlyInvited = cand.status === 'دعوت به مصاحبه';

      if (isCurrentlyInvited) {
        cand.status = 'در انتظار بررسی';
        showToast(`لغو دعوت به مصاحبه «${cand.name}» انجام شد`);
      } else {
        // If candidate was in a seat, vacate it
        const currentSeat = getCandidateAssignedSeat(cid);
        if (currentSeat) {
          seatsState[currentSeat.id] = null;
          saveSeatsState();
        }
        cand.status = 'دعوت به مصاحبه';
        showToast(`📅 «${cand.name}» به مصاحبه حضوری دعوت شد (جهت ارسال ایمیل دعوت روی آیکون ✉️ کلیک کنید)`);
      }

      // Update in saved evaluations
      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
      savedEvals[String(cid)].status = cand.status;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      // Post to backend
      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: cand.status })
      }).catch(() => {});

      // If dossier modal is open for this candidate, update evalStatus
      const evalStatusEl = document.getElementById('evalStatus');
      if (evalStatusEl && selectedCandidate && selectedCandidate.id === cid) {
        evalStatusEl.value = cand.status;
      }

      updateFilterCounts();
      renderSeatsBoard();
      renderRoster();
      renderTimetable();
      if (document.getElementById('tab-analytics')?.classList.contains('active')) {
        renderAnalytics();
      }
    }

    function toggleCandidateRejection(cid) {
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;

      const isCurrentlyRejected = cand.status === 'رد شده' || cand.status === 'عدم پذیرش';

      if (isCurrentlyRejected) {
        cand.status = 'در انتظار مصاحبه';
        showToast(`وضعیت «${cand.name}» به «در انتظار مصاحبه» بازگردانده شد`);
      } else {
        // If candidate was in a seat, vacate it first
        const currentSeat = getCandidateAssignedSeat(cid);
        if (currentSeat) {
          seatsState[currentSeat.id] = null;
          saveSeatsState();
        }
        cand.status = 'رد شده';
        showToast(`❌ «${cand.name}» به عنوان «رد شده» ثبت گردید`);
      }

      // Update in saved evaluations
      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
      savedEvals[String(cid)].status = cand.status;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      // Post to backend
      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: cand.status })
      }).catch(() => {});

      // If dossier modal is open for this candidate, update evalStatus
      const evalStatusEl = document.getElementById('evalStatus');
      if (evalStatusEl && selectedCandidate && selectedCandidate.id === cid) {
        evalStatusEl.value = cand.status;
      }

      updateFilterCounts();
      renderSeatsBoard();
      renderRoster();
      renderTimetable();
    }
    

    function assignCandidateToSeat(cid, seatId) {
      const cand = candidates.find(c => c.id === cid);
      const seat = SEATS_CONFIG.find(s => s.id === seatId);
      if (!cand || !seat) return;

      // If candidate was in another seat, vacate it first
      for (const [sId, cId] of Object.entries(seatsState)) {
        if (cId === cid) seatsState[sId] = null;
      }

      seatsState[seatId] = cid;
      cand.status = 'پذیرفته‌شده قطعی';

      // Update in saved evaluations
      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
      savedEvals[String(cid)].status = cand.status;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: cand.status })
      }).catch(() => {});

      saveSeatsState();
      showToast(`🌟 ${cand.name} با موفقیت در «${seat.title}» پذیرفته شد`);

      if (currentPickerSeatId) renderSeatPickerList();

      renderSeatsBoard();
      renderRoster();
      renderTimetable();
    }

    function vacateSeat(seatId) {
      const cid = seatsState[seatId];
      const seat = SEATS_CONFIG.find(s => s.id === seatId);
      if (cid) {
        const cand = candidates.find(c => c.id === cid);
        if (cand) {
          cand.status = 'در انتظار مصاحبه';
          const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
          if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
          savedEvals[String(cid)].status = cand.status;
          localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

          fetch(`/api/candidate/${cid}/eval`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: cand.status })
          }).catch(() => {});
        }
      }
      seatsState[seatId] = null;
      saveSeatsState();
      showToast(`ظرفیت «${seat?.title || seatId}» با موفقیت تخلیه شد`);

      if (currentPickerSeatId) renderSeatPickerList();

      renderSeatsBoard();
      renderRoster();
      renderTimetable();
    }

    function resetAllSeats() {
      if (!confirm('آیا از خالی‌کردن همه ظرفیت‌های آزمایشگاه مطمئن هستید؟')) return;
      SEATS_CONFIG.forEach(s => {
        const cid = seatsState[s.id];
        if (cid) {
          const cand = candidates.find(c => c.id === cid);
          if (cand) cand.status = 'در انتظار مصاحبه';
        }
        seatsState[s.id] = null;
      });
      saveSeatsState();
      showToast('تمامی ظرفیت‌های آزمایشگاه تخلیه شدند');
      renderSeatsBoard();
      renderRoster();
      renderTimetable();
    }

    // ==========================================
    // CANDIDATES LIST RENDERING (BOARD & ROSTER)
    // ==========================================
    function renderBoardCandidates() {
      const container = document.getElementById('boardCandidatesGrid');
      if (!container) return;
      container.innerHTML = '';
      candidates.forEach(c => container.appendChild(createCandidateCard(c)));
    }

    function createCandidateCard(c) {
      const card = document.createElement('div');
      const assignedSeat = getCandidateAssignedSeat(c.id);
      const isAccepted = assignedSeat !== null;
      const isRejected = c.status === 'رد شده' || c.status === 'عدم پذیرش';
      const isInvited = c.status === 'دعوت به مصاحبه';
      const isStarred = starredIds.has(c.id);

      card.className = `candidate-card ${isAccepted ? 'is-accepted' : ''} ${isRejected ? 'is-rejected' : ''}`;
      card.setAttribute('data-id', c.id);

      const trackClass = c.track_en === 'AI' ? 'ai' : 'sw';

      card.innerHTML = `
        <div class="card-top">
          <div class="card-monogram" style="background: ${c.color};" onclick="openDossierModal(${c.id})" title="مشاهده پرونده کامل ${c.name}">${c.initials}</div>
          <div class="card-title-meta">
            <div class="card-header-row">
              <div class="card-name-wrapper" onclick="openDossierModal(${c.id})" title="کلیک کنید: مشاهده پرونده کامل، سوابق، فایل‌های PDF، متن ایمیل و ارزیابی">
                <h3 class="card-name ${isRejected ? 'name-strikethrough' : ''}">${c.name}</h3>
                <span class="card-dossier-pill">📄 جزئیات پرونده ↗</span>
              </div>
              <button class="btn-star-card ${isStarred ? 'starred' : ''}" onclick="event.stopPropagation(); toggleStar(${c.id}, this)" title="نشان کردن در برگزیده‌ها">
                ★
              </button>
            </div>
            <div class="card-badges-row">
              <span class="badge-pill ${trackClass}">${c.track}</span>
              <span class="badge-pill quota">${c.admission_type}</span>
              ${c.interview_phase ? `<span class="badge-pill phase-${c.interview_phase}">${getPhaseLabelShort(c.interview_phase)}</span>` : ''}
              <span class="badge-pill rank">${c.konkur_arshad.includes('رتبه') || c.konkur_arshad.includes('استعداد') || c.konkur_arshad.includes('روزانه') || c.konkur_arshad.includes('شبانه') || c.konkur_arshad.includes('قبولی') ? c.konkur_arshad : 'رتبه ' + c.konkur_arshad}</span>
              ${isAccepted ? `<span class="badge-pill accepted">✅ ${assignedSeat.title.split(':')[1]?.trim() || assignedSeat.title}</span>` : ''}
              ${isInvited ? '<span class="badge-pill" style="background:#E0F2FE; color:#0284C7; border:1.5px solid #0284C7; font-weight:800;">📅 دعوت به مصاحبه</span>' : ''}
              ${isRejected ? `<span class="badge-pill rejected" style="background:#fee2e2; color:#dc2626; border:1px solid #f87171; font-weight:800;">❌ رد شده${c.eval_notes ? ' (' + c.eval_notes + ')' : ''}</span>` : ''}
            </div>
          </div>
        </div>

        <div class="card-body" onclick="openDossierModal(${c.id})" title="کلیک روی کارت برای باز کردن پرونده کامل، ریزنمرات و فایل PDF">
          <div class="card-info-row">
            <span class="info-label">کارشناسی:</span>
            <span class="info-val">${c.bsc_major} · ${c.bsc_uni}</span>
          </div>
          <div class="card-info-row">
            <span class="info-label">معدل:</span>
            <span class="info-val" style="color: var(--color-stamp); font-size: 14px;">${c.bsc_gpa}</span>
          </div>
          <div class="card-info-row">
            <span class="info-label">دبیرستان:</span>
            <span class="info-val">${c.high_school}</span>
          </div>
          <div class="card-info-row">
            <span class="info-label">مصاحبه:</span>
            <span class="info-val" style="${isRejected ? 'text-decoration: line-through; color: var(--color-ink-muted);' : ''}">${c.interview_slot ? c.interview_slot + ' (حضوری)' : '<span style="color:var(--color-ink-muted);">تعیین نشده</span>'} ${isRejected ? '<span style="color:#dc2626; font-size:11px; font-weight:800;">[لغو شده]</span>' : ''}</span>
          </div>
          <div>
            <div style="font-size: 11px; font-weight: 700; color: var(--color-ink-muted); margin-bottom: 4px;">مهارت‌های شاخص:</div>
            <div class="skills-tags-row">
              ${c.skills.split(',').slice(0, 4).map(s => `<span class="skill-tag">${s.trim()}</span>`).join('')}
            </div>
          </div>
          <div class="card-body-click-prompt">
            <span>📄 مشاهده پرونده کامل، کارنامه و رزومه PDF</span>
            <span class="arrow-hint">←</span>
          </div>
        </div>

        <div class="card-footer">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; padding: 4px 8px; background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 4px; font-size: 11px;">
            <span style="font-weight: 800; color: var(--color-ink-muted);">🎯 فاز اولویت مصاحبه:</span>
            <select class="phase-select phase-${c.interview_phase || 'none'}" onchange="setCandidatePhase(${c.id}, this.value, event)" onclick="event.stopPropagation();" title="تعیین فاز اولویت دعوت به مصاحبه">
              <option value="" ${!c.interview_phase ? 'selected' : ''}>— بدون فاز —</option>
              <option value="phase1" ${c.interview_phase === 'phase1' ? 'selected' : ''}>🟣 فاز ۱ (اولویت اول)</option>
              <option value="phase2" ${c.interview_phase === 'phase2' ? 'selected' : ''}>🔵 فاز ۲ (اولویت دوم)</option>
              <option value="phase3" ${c.interview_phase === 'phase3' ? 'selected' : ''}>🟠 فاز ۳ (اولویت سوم)</option>
            </select>
          </div>

          <div style="display: grid; grid-template-columns: 1.1fr 1.35fr 0.75fr; gap: 5px; margin-bottom: 8px;">
            <button class="btn-accept-seat ${isAccepted ? 'is-assigned' : ''}" style="margin-bottom: 0; padding: 6px 3px; font-size: 11px; white-space: nowrap;" onclick="toggleCandidateAcceptance(${c.id})">
              ${isAccepted ? '🌟 پذیرفته (لغو)' : '✅ قبول'}
            </button>
            <button class="card-btn" style="padding: 6px 3px; font-size: 11px; font-weight: 800; white-space: nowrap; ${isInvited ? 'background: #0284C7; border-color: #0284C7; color: #fff;' : 'color: #0284C7; border-color: #7DD3FC; background: #F0F9FF;'}" onclick="toggleCandidateInvitation(${c.id})" title="${isInvited ? 'لغو وضعیت دعوت به مصاحبه' : 'دعوت به مصاحبه حضوری'}">
              ${isInvited ? '✓ لغو دعوت' : '📅 دعوت به مصاحبه'}
            </button>
            <button class="card-btn" style="padding: 6px 3px; font-weight: 800; font-size: 11px; white-space: nowrap; ${isRejected ? 'background: #dc2626; color: #fff; border-color: #dc2626;' : 'color: #dc2626; border-color: #fca5a5; background: #fff;'}" onclick="toggleCandidateRejection(${c.id})" title="${isRejected ? 'لغو وضعیت رد' : 'رد کردن متقاضی'}">
              ${isRejected ? 'لغو رد' : '❌ رد'}
            </button>
          </div>

          <div class="card-actions-row">
            <button class="card-btn" style="padding: 3px 8px;" onclick="event.stopPropagation(); openEmailModal(${c.id})" title="قالب ایمیل و مکاتبه">
              ✉️ مکاتبه
            </button>
            <button class="card-btn primary" onclick="openDossierModal(${c.id})" title="مشاهده پرونده کامل، کارنامه و فایل‌های پیوست PDF">
              📄 پرونده و PDF ↗
            </button>
            <button class="card-btn" onclick="openDossierModal(${c.id}, 'email')" title="مشاهده متن کامل ایمیل متقاضی">
              ✉️ متن ایمیل
            </button>
            <button class="card-btn" onclick="openDossierModal(${c.id}, 'eval')" title="فرم ارزیابی و ثبت نمره مصاحبه">
              ✍️ ارزیابی
            </button>
          </div>
        </div>
      `;
      return card;
    }

    function toggleStar(cid, btn) {
      if (starredIds.has(cid)) {
        starredIds.delete(cid);
        btn.classList.remove('starred');
      } else {
        starredIds.add(cid);
        btn.classList.add('starred');
        showToast('⭐ به لیست کاندیداهای برگزیده اضافه شد');
      }
      localStorage.setItem('admission_starred', JSON.stringify(Array.from(starredIds)));
      updateFilterCounts();
      if (currentFilter === 'starred') renderRoster();
    }
    let currentTrackFilter = 'all'; // 'all', 'AI', 'Software'

    function setTrackFilter(track, btn) {
      currentTrackFilter = track;
      document.querySelectorAll('.track-tab-btn').forEach(b => b.classList.remove('active'));
      if (btn) {
        btn.classList.add('active');
      } else {
        if (track === 'all') document.getElementById('btnTrackAll')?.classList.add('active');
        if (track === 'AI') document.getElementById('btnTrackAI')?.classList.add('active');
        if (track === 'Software') document.getElementById('btnTrackSW')?.classList.add('active');
      }
      renderRoster();
    }
    

    function setFilter(filterType, btn) {
      currentFilter = filterType;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderRoster();
    }

    function setViewMode(mode) {
      currentViewMode = mode;
      document.getElementById('btnViewCards').classList.toggle('active', mode === 'cards');
      document.getElementById('btnViewTable').classList.toggle('active', mode === 'table');
      document.getElementById('rosterCardsContainer').style.display = mode === 'cards' ? 'grid' : 'none';
      const hintBar = document.getElementById('rosterCardsHintBar');
      if (hintBar) hintBar.style.display = mode === 'cards' ? 'flex' : 'none';
      document.getElementById('rosterTableContainer').style.display = mode === 'table' ? 'block' : 'none';
      renderRoster();
    }

    function getFilteredCandidates() {
      const query = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
      const sortVal = document.getElementById('sortSelect')?.value || 'priority';

      let list = candidates.filter(c => {
        // 1. Dedicated Track Filter (All, AI only, Software only)
        if (currentTrackFilter === 'AI' && c.track_en !== 'AI') return false;
        if (currentTrackFilter === 'Software' && c.track_en !== 'Software') return false;

        // 2. Phase Prioritization Filter
        if (currentPhaseFilter === 'phase1' && c.interview_phase !== 'phase1') return false;
        if (currentPhaseFilter === 'phase2' && c.interview_phase !== 'phase2') return false;
        if (currentPhaseFilter === 'phase3' && c.interview_phase !== 'phase3') return false;
        if (currentPhaseFilter === 'nophase' && c.interview_phase) return false;

        // 3. Status & Quota Filters
        if (currentFilter === 'accepted' && !isCandidateAssigned(c.id)) return false;
        if (currentFilter === 'invited' && c.status !== 'دعوت به مصاحبه') return false;
        if (currentFilter === 'rejected' && !(c.status === 'رد شده' || c.status === 'عدم پذیرش')) return false;
        if (currentFilter === 'pending' && (c.status === 'رد شده' || c.status === 'عدم پذیرش' || c.status === 'دعوت به مصاحبه' || isCandidateAssigned(c.id))) return false;
        if (currentFilter === 'AI' && c.track_en !== 'AI') return false;
        if (currentFilter === 'Software' && c.track_en !== 'Software') return false;
        if (currentFilter === 'rozaneh' && !(c.admission_type.includes('روزانه') || c.quota.includes('روزانه') || c.quota.includes('استعداد') || c.quota.includes('بورس'))) return false;
        if (currentFilter === 'shabaneh' && !(c.admission_type.includes('شبانه') || c.quota.includes('شبانه'))) return false;
        if (currentFilter === 'talented' && !(c.admission_type.includes('استعداد') || c.quota.includes('استعداد'))) return false;
        if (currentFilter === 'starred' && !starredIds.has(c.id)) return false;

        if (query) {
          const str = (c.name + ' ' + c.bsc_uni + ' ' + c.high_school + ' ' + c.skills + ' ' + c.konkur_arshad + ' ' + (c.interests||'')).toLowerCase();
          if (!str.includes(query)) return false;
        }
        return true;
      });

      list.sort((a, b) => {
        if (sortVal === 'priority') {
          return defaultCandidateSort(a, b);
        } else if (sortVal === 'sw_first') {
          const isSwA = isCandidateSoftware(a) ? 1 : 2;
          const isSwB = isCandidateSoftware(b) ? 1 : 2;
          if (isSwA !== isSwB) return isSwA - isSwB;
          return defaultCandidateSort(a, b);
        } else if (sortVal === 'phase') {
          const pOrder = { 'phase1': 1, 'phase2': 2, 'phase3': 3 };
          const wa = pOrder[a.interview_phase] || 99;
          const wb = pOrder[b.interview_phase] || 99;
          if (wa !== wb) return wa - wb;
          return defaultCandidateSort(a, b);
        } else if (sortVal === 'rank_asc') {
          return (a.rank_val || 999) - (b.rank_val || 999);
        } else if (sortVal === 'gpa_desc') {
          return (b.gpa_val || 0) - (a.gpa_val || 0);
        } else if (sortVal === 'name') {
          return a.name.localeCompare(b.name, 'fa');
        } else if (sortVal === 'slot') {
          return (a.interview_slot || '').localeCompare(b.interview_slot || '', 'fa');
        }
        return defaultCandidateSort(a, b);
      });

      return list;
    }

    function renderRoster() {
      const list = getFilteredCandidates();

      if (currentViewMode === 'cards') {
        const container = document.getElementById('rosterCardsContainer');
        container.innerHTML = '';
        if (list.length === 0) {
          container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; font-weight: 700;">موردی با این مشخصات یافت نشد.</div>';
          return;
        }
        list.forEach(c => container.appendChild(createCandidateCard(c)));
      } else {
        const tbody = document.getElementById('rosterTableBody');
        tbody.innerHTML = '';
        if (list.length === 0) {
          tbody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 20px;">موردی یافت نشد.</td></tr>';
          return;
        }
        list.forEach((c, idx) => {
          const tr = document.createElement('tr');
          const assignedSeat = getCandidateAssignedSeat(c.id);
          const isAccepted = assignedSeat !== null;
          const isRejected = c.status === 'رد شده' || c.status === 'عدم پذیرش';
          const isInvited = c.status === 'دعوت به مصاحبه';

          tr.className = isRejected ? 'row-rejected' : (isAccepted ? 'row-accepted' : '');
          tr.onclick = () => openDossierModal(c.id);
          tr.innerHTML = `
            <td style="text-align: center;">${idx + 1}</td>
            <td>
              <b class="${isRejected ? 'name-strikethrough' : ''}">${c.name}</b>
              ${isRejected && c.eval_notes ? `<div style="font-size: 10px; color: #dc2626; font-weight: 700; margin-top: 2px;">⚠️ ${c.eval_notes}</div>` : ''}
            </td>
            <td style="text-align: center; white-space: nowrap;" onclick="event.stopPropagation();">
              <select class="phase-select phase-${c.interview_phase || 'none'}" onchange="setCandidatePhase(${c.id}, this.value, event)" title="تعیین فاز اولویت مصاحبه">
                <option value="" ${!c.interview_phase ? 'selected' : ''}>— بدون فاز —</option>
                <option value="phase1" ${c.interview_phase === 'phase1' ? 'selected' : ''}>🟣 فاز ۱</option>
                <option value="phase2" ${c.interview_phase === 'phase2' ? 'selected' : ''}>🔵 فاز ۲</option>
                <option value="phase3" ${c.interview_phase === 'phase3' ? 'selected' : ''}>🟠 فاز ۳</option>
              </select>
            </td>
            <td style="text-align: center; white-space: nowrap;"><span class="badge-pill ${c.track_en === 'AI' ? 'ai' : 'sw'}" style="white-space: nowrap; display: inline-block;">${c.track}</span></td>
            <td style="font-size: 11px;">${c.quota}</td>
            <td style="text-align: center; font-size: 11px;"><b>${c.konkur_arshad}</b></td>
            <td style="font-size: 11px;">${c.bsc_uni}</td>
            <td style="color: var(--color-stamp); font-weight: 800; text-align: center;">${c.bsc_gpa}</td>
            <td style="text-align: center;">
              ${isAccepted ? `<span class="badge-pill accepted" style="white-space: nowrap; font-size: 10px;">✅ ${assignedSeat.title.split(':')[1]?.trim() || assignedSeat.title}</span>` 
                : (isInvited ? '<span class="badge-pill" style="background: #E0F2FE; color: #0284C7; border: 1.5px solid #0284C7; font-size: 10px; font-weight: 800; white-space: nowrap;">📅 دعوت به مصاحبه</span>' 
                : (isRejected ? `<span class="badge-pill" style="background: #FEE2E2; color: #DC2626; border: 1px solid #F87171; font-size: 10px; white-space: nowrap;">❌ رد شده${c.eval_notes ? ' (' + c.eval_notes + ')' : ''}</span>` 
                : '<span style="color:var(--color-ink-muted); font-size: 11px;">در انتظار بررسی</span>'))}
            </td>
            <td style="text-align: center; font-size: 10.5px; white-space: nowrap; ${isRejected ? 'text-decoration: line-through; color: var(--color-ink-muted);' : ''}" onclick="event.stopPropagation();">
              ${c.interview_slot ? `
                <div style="font-weight: 800; color: #213A79; font-size: 10.5px; line-height: 1.3;">${c.interview_slot}</div>
                ${isRejected ? '<span style="color:#dc2626; font-size:9.5px; font-weight:800;">(لغو شده)</span>' : `
                <button class="card-btn" style="padding: 1px 6px; font-size: 9.5px; white-space: nowrap; margin-top: 3px;" onclick="openShamsiPicker(${c.id})">📅 تغییر زمان</button>`}
              ` : `
                <span style="color:var(--color-ink-muted); font-size:10.5px; display:block; margin-bottom: 2px;">تعیین نشده</span>
                ${!isRejected ? `<button class="card-btn" style="padding: 1px 6px; font-size: 9.5px; white-space: nowrap;" onclick="openShamsiPicker(${c.id})">📅 تعیین زمان</button>` : ''}
              `}
            </td>
            <td style="text-align: center; white-space: nowrap;">
              <div style="display: inline-flex; gap: 3px; align-items: center; justify-content: center;">
                <button class="card-btn ${isAccepted ? 'primary' : ''}" style="padding: 2px 5px; font-size: 10px; white-space: nowrap; ${isAccepted ? 'background: var(--color-success); border-color: var(--color-success); color: #fff;' : ''}" onclick="event.stopPropagation(); toggleCandidateAcceptance(${c.id})" title="${isAccepted ? 'لغو قبولی این متقاضی' : 'قبول و اختصاص ظرفیت به متقاضی'}">
                  ${isAccepted ? 'لغو قبول' : 'قبول'}
                </button>
                <button class="card-btn" style="padding: 2px 5px; font-size: 10px; white-space: nowrap; ${isInvited ? 'background: #0284C7; border-color: #0284C7; color: #fff; font-weight: 800;' : 'color: #0284C7; border-color: #7DD3FC; background: #F0F9FF;'}" onclick="event.stopPropagation(); toggleCandidateInvitation(${c.id})" title="${isInvited ? 'لغو وضعیت دعوت به مصاحبه' : 'دعوت به مصاحبه حضوری'}">
                  ${isInvited ? '✓ دعوت‌شده' : 'دعوت'}
                </button>
                <button class="card-btn" style="padding: 2px 5px; font-size: 10px; white-space: nowrap; ${isRejected ? 'background: #dc2626; border-color: #dc2626; color: #fff;' : 'color: #dc2626; border-color: #fca5a5;'}" onclick="event.stopPropagation(); toggleCandidateRejection(${c.id})" title="${isRejected ? 'لغو وضعیت رد (بازگشت به در انتظار)' : 'رد کردن این متقاضی'}">
                  ${isRejected ? 'لغو رد' : 'رد'}
                </button>
              </div>
            </td>
            <td style="text-align: center;">
              <div style="display: flex; gap: 3px; justify-content: center;">
                <button class="card-btn" style="padding: 2px 6px; font-size: 11px; white-space: nowrap;" onclick="event.stopPropagation(); openEmailModal(${c.id})" title="قالب‌ساز خودکار ایمیل">✉️</button>
                <button class="card-btn" style="padding: 2px 6px; font-size: 11px; white-space: nowrap;" onclick="event.stopPropagation(); openDossierModal(${c.id})">مشاهده</button>
              </div>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    }

    function renderTimetable() {}

    function setFilesTrackFilter(track) {
      currentFilesTrackFilter = track;
      document.getElementById('btnFilesFilterAll')?.classList.toggle('active', track === 'all');
      document.getElementById('btnFilesFilterAI')?.classList.toggle('active', track === 'AI');
      document.getElementById('btnFilesFilterSW')?.classList.toggle('active', track === 'Software');
      renderFilesExplorer();
    }

    function renderFilesExplorer() {
      const tbody = document.getElementById('filesTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      const query = (document.getElementById('filesSearchInput')?.value || '').trim().toLowerCase();

      // Filter candidates by track and query
      let list = candidates.filter(c => {
        if (currentFilesTrackFilter === 'AI' && c.track_en !== 'AI') return false;
        if (currentFilesTrackFilter === 'Software' && c.track_en !== 'Software') return false;
        if (query) {
          const fileNames = (c.files || []).map(f => f.name).join(' ');
          const str = (c.name + ' ' + c.track + ' ' + c.folder_rel + ' ' + fileNames).toLowerCase();
          if (!str.includes(query)) return false;
        }
        return true;
      });

      // Default track-based ordering
      list.sort(defaultCandidateSort);

      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 24px; color: var(--color-ink-muted); font-weight: 700;">فایل یا متقاضی منطبق یافت نشد.</td></tr>';
        return;
      }

      list.forEach((c, idx) => {
        const tr = document.createElement('tr');
        const assignedSeat = getCandidateAssignedSeat(c.id);
        const isRejected = c.status === 'رد شده' || c.status === 'عدم پذیرش';
        tr.className = isRejected ? 'row-rejected' : '';
        const pdfFiles = c.files.filter(f => f.is_pdf);
        const otherFiles = c.files.filter(f => !f.is_pdf && !f.name.includes('main.txt'));

        tr.innerHTML = `
          <td style="text-align: center;">${idx + 1}</td>
          <td>
            <b class="${isRejected ? 'name-strikethrough' : ''}">${c.name}</b>
            ${isRejected && c.eval_notes ? `<div style="font-size: 10px; color: #dc2626; font-weight: 700; margin-top: 2px;">⚠️ ${c.eval_notes}</div>` : ''}
          </td>
          <td style="text-align: center; white-space: nowrap;"><span class="badge-pill ${c.track_en === 'AI' ? 'ai' : 'sw'}" style="white-space: nowrap; display: inline-block;">${c.track}</span></td>
          <td style="font-size: 11px; direction: ltr; text-align: left; word-break: break-all;">${c.folder_rel}</td>
          <td>
            <div style="display: flex; flex-direction: column; gap: 3px;">
              ${pdfFiles.map((pf, pIdx) => `
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 4px; background: #FFF; border: 1px solid var(--color-ink); padding: 3px 6px; border-radius: 2px;">
                  <a href="${pf.rel_url}" target="_blank" style="color: var(--color-ink); text-decoration: none; font-weight: 700; font-size: 11px; display: flex; align-items: center; gap: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="دانلود / مشاهده مستقیم ${pf.name}">
                    <span>📄</span>
                    <span style="direction: ltr; text-align: left; overflow: hidden; text-overflow: ellipsis;">${pf.name}</span>
                  </a>
                  <div style="display: flex; align-items: center; gap: 4px; flex-shrink: 0;">
                    <span style="font-size: 9.5px; color: var(--color-ink-muted);">${pf.size_str}</span>
                    <button class="card-btn ${pIdx === 0 ? 'primary' : ''}" style="padding: 1px 5px; font-size: 10px; white-space: nowrap;" onclick="event.stopPropagation(); openDossierWithSpecificPdf(${c.id}, '${pf.rel_url}')">
                      پیش‌نمایش
                    </button>
                  </div>
                </div>
              `).join('')}
            </div>
          </td>
          <td>
            ${otherFiles.length > 0 ? `
              <div style="display: flex; flex-direction: column; gap: 3px;">
                ${otherFiles.map(of => `
                  <a href="${of.rel_url}" target="_blank" class="card-btn" style="display: inline-flex; align-items: center; gap: 3px; font-size: 10.5px; padding: 2px 5px;">
                    📎 ${of.name} (${of.size_str})
                  </a>
                `).join('')}
              </div>
            ` : '<span style="color: var(--color-ink-muted);">-</span>'}
          </td>
          <td style="text-align: center;">
            <button class="card-btn" style="padding: 3px 6px; font-size: 10.5px; white-space: nowrap;" onclick="openDossierModal(${c.id}, 'email')">
              ✉️ مشاهده ایمیل
            </button>
          </td>
          <td style="text-align: center;">
            <button class="card-btn primary" style="padding: 3px 6px; font-size: 10.5px; white-space: nowrap;" onclick="openDossierModal(${c.id})">
              پرونده
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function openDossierModal(cid, targetTab = 'overview') {
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;
      selectedCandidate = cand;

      const assignedSeat = getCandidateAssignedSeat(cid);
      const isRejected = cand.status === 'رد شده' || cand.status === 'عدم پذیرش';

      document.getElementById('modalMonogram').textContent = cand.initials;
      document.getElementById('modalMonogram').style.background = cand.color;
      const modalNameEl = document.getElementById('modalName');
      modalNameEl.textContent = cand.name;
      if (isRejected) {
        modalNameEl.classList.add('name-strikethrough');
      } else {
        modalNameEl.classList.remove('name-strikethrough');
      }
      document.getElementById('modalSubtitle').textContent = `${cand.track} | ${cand.admission_type} | رتبه ${cand.konkur_arshad} | کارشناسی ${cand.bsc_uni}${isRejected ? ' | [❌ وضعیت: رد شده / انصراف]' : ''}`;

      document.getElementById('modalPhone').textContent = cand.phone || '-';
      document.getElementById('modalEmail').textContent = cand.email || '-';
      document.getElementById('modalSocial').textContent = cand.social || '-';
      document.getElementById('modalBsc').textContent = `${cand.bsc_major} دانشگاه ${cand.bsc_uni} (رتبه کارشناسی: ${cand.konkur_bsc || '-'})`;
      document.getElementById('modalGpa').textContent = cand.bsc_gpa;
      document.getElementById('modalKonkur').textContent = cand.konkur_arshad;
      document.getElementById('modalHighSchool').textContent = cand.high_school;
      document.getElementById('modalExp').textContent = cand.exp || cand.notes;
      document.getElementById('modalInterests').textContent = cand.interests || 'در رزومه قید شده است.';
      document.getElementById('modalNotes').textContent = cand.notes;

      // Seat status box
      const seatBox = document.getElementById('modalSeatStatusBox');
      if (assignedSeat) {
        seatBox.innerHTML = `
          <div style="font-weight: 800; color: var(--color-success); font-size: 14px; margin-bottom: 4px;">
            ✅ پذیرفته‌شده در ${assignedSeat.title}
          </div>
          <button type="button" class="card-btn" style="color: var(--color-stamp);" onclick="vacateSeat('${assignedSeat.id}'); openDossierModal(${cand.id}, 'overview');">
            ✕ لغو قبولی و تخلیه ظرفیت
          </button>
        `;
      } else if (isRejected) {
        seatBox.innerHTML = `
          <div style="font-weight: 800; color: #DC2626; font-size: 14px; margin-bottom: 4px;">
            ❌ پرونده رد شده / انصراف داده شده
          </div>
          <div style="font-size: 12px; color: #991B1B; margin-bottom: 8px;">
            ${cand.eval_notes ? `علت / یادداشت: ${cand.eval_notes}` : 'عدم پذیرش در این دوره آزمایشگاه'}
          </div>
          <button type="button" class="card-btn" style="color: var(--color-ink);" onclick="toggleCandidateRejection(${cand.id}); openDossierModal(${cand.id}, 'overview');">
            🔄 بازگردانی پرونده به جریان ارزیابی
          </button>
        `;
      } else {
        seatBox.innerHTML = `
          <div style="font-weight: 700; color: var(--color-ink-muted); margin-bottom: 6px;">
            وضعیت فعلی: در انتظار پذیرش و تخصیص ظرفیت
          </div>
          <button type="button" class="btn-accept-seat" onclick="toggleCandidateAcceptance(${cand.id}); openDossierModal(${cand.id}, 'overview');">
            ✅ قبول و تخصیص ظرفیت آزمایشگاه
          </button>
        `;
      }

      document.getElementById('modalSkillsTags').innerHTML = (cand.skills || '').split(',').map(s => `<span class="skill-tag">${s.trim()}</span>`).join('');

      const pdfSelector = document.getElementById('pdfSelectorBtns');
      pdfSelector.innerHTML = '';
      const pdfFiles = cand.files.filter(f => f.is_pdf);
      
      if (pdfFiles.length > 0) {
        pdfFiles.forEach((pf, idx) => {
          const btn = document.createElement('button');
          btn.className = 'card-btn' + (idx === 0 ? ' primary' : '');
          btn.textContent = `📄 ${pf.name} (${pf.size_str})`;
          btn.onclick = () => {
            pdfSelector.querySelectorAll('.card-btn').forEach(b => b.classList.remove('primary'));
            btn.classList.add('primary');
            setPdfViewer(pf.rel_url);
          };
          pdfSelector.appendChild(btn);
        });
        setPdfViewer(cand.primary_pdf || pdfFiles[0].rel_url);
      } else {
        pdfSelector.innerHTML = '<span style="font-size: 13px; color: var(--color-ink-muted);">فایل PDF یافت نشد.</span>';
        setPdfViewer('');
      }

      document.getElementById('emailFrom').textContent = cand.name + ' (' + (cand.email || '') + ')';
      document.getElementById('emailSubject').textContent = `[ارشد ۱۴۰۵] - ${cand.name} - ${cand.track} - ${cand.admission_type}`;
      document.getElementById('emailBodyText').textContent = cand.email_body || 'متن ایمیلی ثبت نشده است.';

      // Eval pane form
      document.getElementById('evalCandidateId').value = cand.id;
      document.getElementById('evalStatus').value = cand.status || (assignedSeat ? 'پذیرفته‌شده قطعی' : 'در انتظار مصاحبه');
      document.getElementById('evalScore').value = cand.score || '';
      document.getElementById('evalScoreRange').value = cand.score || 0;
      document.getElementById('evalSlot').value = cand.interview_slot || '';
      document.getElementById('evalNotes').value = cand.eval_notes || '';
      const evalPhaseEl = document.getElementById('evalPhase');
      if (evalPhaseEl) evalPhaseEl.value = cand.interview_phase || '';

      // Populate seat select dropdown strictly by track and quota
      const evalSeatSel = document.getElementById('evalSeatSelect');
      const isCandSw = isCandidateSoftware(cand);
      const isCandShab = isCandidateShabaneh(cand);

      let eligibleSeats = [];
      if (isCandSw) {
        eligibleSeats = SEATS_CONFIG.filter(s => s.group === 'sw_roz');
      } else {
        eligibleSeats = SEATS_CONFIG.filter(s => isCandShab ? s.group === 'ai_shab' : s.group === 'ai_roz');
      }

      // If candidate is already in an assigned seat outside current filter, keep that seat visible
      if (assignedSeat && !eligibleSeats.some(s => s.id === assignedSeat.id)) {
        eligibleSeats.push(assignedSeat);
      }

      evalSeatSel.innerHTML = `
        <option value="">-- بدون تخصیص ظرفیت (در انتظار) --</option>
        ${eligibleSeats.map(s => `
          <option value="${s.id}" ${assignedSeat?.id === s.id ? 'selected' : (seatsState[s.id] !== null ? 'disabled' : '')}>
            ${s.title} ${seatsState[s.id] !== null && assignedSeat?.id !== s.id ? '(پر شده توسط متقاضی دیگر)' : ''}
          </option>
        `).join('')}
      `;

      const tabBtns = document.querySelectorAll('.modal-tab-btn');
      tabBtns.forEach(b => {
        if (b.getAttribute('onclick')?.includes(targetTab)) {
          switchModalTab(targetTab, b);
        }
      });

      document.getElementById('dossierModalOverlay').classList.add('active');
    }

    function setPdfViewer(url) {
      const iframe = document.getElementById('pdfIframe');
      const downloadBtn = document.getElementById('btnDownloadCurrentPdf');
      iframe.src = url;
      downloadBtn.href = url;
    }

    function closeDossierModal() {
      document.getElementById('dossierModalOverlay').classList.remove('active');
      document.getElementById('pdfIframe').src = '';
    }

    function handleModalOverlayClick(e) {
      if (e.target.id === 'dossierModalOverlay') closeDossierModal();
    }

    function handleEvalSubmit(e) {
      e.preventDefault();
      const cid = parseInt(document.getElementById('evalCandidateId').value);
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;

      const chosenSeatId = document.getElementById('evalSeatSelect').value;
      if (chosenSeatId) {
        assignCandidateToSeat(cid, chosenSeatId);
      } else {
        const currentSeat = getCandidateAssignedSeat(cid);
        if (currentSeat) vacateSeat(currentSeat.id);
      }

      const evalData = {
        status: document.getElementById('evalStatus').value,
        score: document.getElementById('evalScore').value,
        interview_slot: document.getElementById('evalSlot').value,
        eval_notes: document.getElementById('evalNotes').value,
        interview_phase: document.getElementById('evalPhase')?.value || null
      };

      Object.assign(cand, evalData);

      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      savedEvals[String(cid)] = evalData;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(evalData)
      }).catch(() => {});

      showToast('✔️ ارزیابی و وضعیت با موفقیت ذخیره شد');
      closeDossierModal();
      renderSeatsBoard();
      renderRoster();
      renderTimetable();
    }

    function copyContactText(text) {
      if (!text || text === '--' || text === '-' || text.startsWith('-')) {
        showToast('⚠️ اطلاعاتی برای کپی ثبت نشده است');
        return;
      }
      navigator.clipboard.writeText(text).then(() => {
        showToast('📋 کپی شد: ' + text);
      }).catch(() => {});
    }

    function showToast(text) {
      const toast = document.getElementById('toastMsg');
      document.getElementById('toastText').textContent = text;
      toast.style.display = 'flex';
      setTimeout(() => { toast.style.display = 'none'; }, 2500);
    }

    
    // ==========================================
    // MODERN SHAMSI DATE & TIME PICKER LOGIC
    // ==========================================
    const SHAMSI_PRESET_DAYS = [
      { dayOfWeek: 'سه‌شنبه', dayNum: '۱۹', month: 'آبان', title: 'سه‌شنبه ۱۹ آبان' },
      { dayOfWeek: 'چهارشنبه', dayNum: '۲۰', month: 'آبان', title: 'چهارشنبه ۲۰ آبان' },
      { dayOfWeek: 'پنج‌شنبه', dayNum: '۲۱', month: 'آبان', title: 'پنج‌شنبه ۲۱ آبان' },
      { dayOfWeek: 'شنبه', dayNum: '۲۴', month: 'آبان', title: 'شنبه ۲۴ آبان' },
      { dayOfWeek: 'یکشنبه', dayNum: '۲۵', month: 'آبان', title: 'یکشنبه ۲۵ آبان' },
      { dayOfWeek: 'دوشنبه', dayNum: '۲۶', month: 'آبان', title: 'دوشنبه ۲۶ آبان' },
      { dayOfWeek: 'سه‌شنبه', dayNum: '۲۷', month: 'آبان', title: 'سه‌شنبه ۲۷ آبان' },
      { dayOfWeek: 'چهارشنبه', dayNum: '۲۸', month: 'آبان', title: 'چهارشنبه ۲۸ آبان' }
    ];

    const SHAMSI_MORNING_SLOTS = [
      { text: '۰۸:۳۰ تا ۰۸:۵۰', startH: 8, startM: 30, dur: 20 },
      { text: '۰۸:۵۰ تا ۰۹:۱۰', startH: 8, startM: 50, dur: 20 },
      { text: '۰۹:۱۰ تا ۰۹:۳۰', startH: 9, startM: 10, dur: 20 },
      { text: '۰۹:۳۰ تا ۰۹:۵۰', startH: 9, startM: 30, dur: 20 },
      { text: '۰۹:۵۰ تا ۱۰:۱۰', startH: 9, startM: 50, dur: 20 },
      { text: '۱۰:۱۰ تا ۱۰:۳۰', startH: 10, startM: 10, dur: 20 },
      { text: '۱۰:۳۰ تا ۱۰:۵۰', startH: 10, startM: 30, dur: 20 },
      { text: '۱۰:۵۰ تا ۱۱:۱۰', startH: 10, startM: 50, dur: 20 },
      { text: '۱۱:۱۰ تا ۱۱:۳۰', startH: 11, startM: 10, dur: 20 },
      { text: '۱۱:۳۰ تا ۱۱:۵۰', startH: 11, startM: 30, dur: 20 },
      { text: '۱۱:۵۰ تا ۱۲:۱۰', startH: 11, startM: 50, dur: 20 },
      { text: '۱۲:۱۰ تا ۱۲:۳۰', startH: 12, startM: 10, dur: 20 }
    ];

    const SHAMSI_AFTERNOON_SLOTS = [
      { text: '۱۳:۳۰ تا ۱۳:۵۰', startH: 13, startM: 30, dur: 20 },
      { text: '۱۳:۵۰ تا ۱۴:۱۰', startH: 13, startM: 50, dur: 20 },
      { text: '۱۴:۱۰ تا ۱۴:۳۰', startH: 14, startM: 10, dur: 20 },
      { text: '۱۴:۳۰ تا ۱۴:۵۰', startH: 14, startM: 30, dur: 20 },
      { text: '۱۴:۵۰ تا ۱۵:۱۰', startH: 14, startM: 50, dur: 20 },
      { text: '۱۵:۱۰ تا ۱۵:۳۰', startH: 15, startM: 10, dur: 20 },
      { text: '۱۵:۳۰ تا ۱۵:۵۰', startH: 15, startM: 30, dur: 20 },
      { text: '۱۵:۵۰ تا ۱۶:۱۰', startH: 15, startM: 50, dur: 20 },
      { text: '۱۶:۱۰ تا ۱۶:۳۰', startH: 16, startM: 10, dur: 20 },
      { text: '۱۶:۳۰ تا ۱۶:۵۰', startH: 16, startM: 30, dur: 20 },
      { text: '۱۶:۵۰ تا ۱۷:۱۰', startH: 16, startM: 50, dur: 20 }
    ];

    let currentShamsiCid = null;
    let selectedShamsiDate = 'سه‌شنبه ۱۹ آبان ۱۴۰۵';
    let selectedShamsiTime = '۰۹:۱۰ تا ۰۹:۳۰';

    function initShamsiPickerDom() {
      // Populate Days Chips
      const daysContainer = document.getElementById('shamsiDateChipsContainer');
      if (daysContainer && daysContainer.children.length === 0) {
        SHAMSI_PRESET_DAYS.forEach((d, idx) => {
          const chip = document.createElement('div');
          chip.className = `shamsi-date-chip ${idx === 0 ? 'active' : ''}`;
          chip.onclick = () => selectShamsiDate(d.dayOfWeek, d.dayNum, d.month, chip);
          chip.innerHTML = `
            <div class="shamsi-date-chip-day">${d.dayOfWeek}</div>
            <div class="shamsi-date-chip-num">${d.dayNum} ${d.month}</div>
          `;
          daysContainer.appendChild(chip);
        });
      }

      // Populate Morning Chips
      const mornContainer = document.getElementById('shamsiMorningChipsContainer');
      if (mornContainer && mornContainer.children.length === 0) {
        SHAMSI_MORNING_SLOTS.forEach((slot, idx) => {
          const chip = document.createElement('div');
          chip.className = `shamsi-time-chip ${idx === 0 ? 'active' : ''}`;
          chip.textContent = slot.text;
          chip.onclick = () => selectShamsiTime(slot.text, chip);
          mornContainer.appendChild(chip);
        });
      }

      // Populate Afternoon Chips
      const aftContainer = document.getElementById('shamsiAfternoonChipsContainer');
      if (aftContainer && aftContainer.children.length === 0) {
        SHAMSI_AFTERNOON_SLOTS.forEach((slot) => {
          const chip = document.createElement('div');
          chip.className = 'shamsi-time-chip';
          chip.textContent = slot.text;
          chip.onclick = () => selectShamsiTime(slot.text, chip);
          aftContainer.appendChild(chip);
        });
      }

      // Populate Custom Selects if empty
      const daySelect = document.getElementById('shamsiDayOfMonth');
      if (daySelect && daySelect.options.length === 0) {
        for (let d = 1; d <= 31; d++) {
          const opt = document.createElement('option');
          opt.value = d < 10 ? '۰' + d : String(d);
          opt.textContent = `${d} ام`;
          if (d === 10) opt.selected = true;
          daySelect.appendChild(opt);
        }
      }

      const hourSelect = document.getElementById('shamsiStartHour');
      if (hourSelect && hourSelect.options.length === 0) {
        for (let h = 8; h <= 20; h++) {
          const opt = document.createElement('option');
          const hStr = h < 10 ? '0' + h : String(h);
          opt.value = hStr;
          opt.textContent = `ساعت ${hStr}:۰۰`;
          if (h === 8) opt.selected = true;
          hourSelect.appendChild(opt);
        }
      }
    }

    function selectShamsiDate(dayOfWeek, dayNum, month, chipEl) {
      document.querySelectorAll('.shamsi-date-chip').forEach(c => c.classList.remove('active'));
      if (chipEl) chipEl.classList.add('active');
      selectedShamsiDate = `${dayOfWeek} ${dayNum} ${month} ۱۴۰۵`;

      // Sync custom selectors
      const dowSel = document.getElementById('shamsiDayOfWeek');
      const domSel = document.getElementById('shamsiDayOfMonth');
      const mSel = document.getElementById('shamsiMonth');
      if (dowSel) dowSel.value = dayOfWeek;
      if (domSel) domSel.value = dayNum.length === 1 ? '۰' + dayNum : dayNum;
      if (mSel) mSel.value = month;

      updateShamsiSummaryDisplay();
    }

    function selectShamsiTime(slotText, chipEl) {
      document.querySelectorAll('.shamsi-time-chip').forEach(c => c.classList.remove('active'));
      if (chipEl) chipEl.classList.add('active');
      selectedShamsiTime = slotText;
      updateShamsiSummaryDisplay();
    }

    function onCustomDateInputChanged() {
      const dow = document.getElementById('shamsiDayOfWeek').value;
      const dom = document.getElementById('shamsiDayOfMonth').value;
      const m = document.getElementById('shamsiMonth').value;
      selectedShamsiDate = `${dow} ${dom} ${m} ۱۴۰۵`;

      // Update active chip if matches
      document.querySelectorAll('.shamsi-date-chip').forEach(c => {
        if (c.textContent.includes(dow) && c.textContent.includes(dom)) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });

      updateShamsiSummaryDisplay();
    }

    function onCustomTimeInputChanged() {
      const startH = parseInt(document.getElementById('shamsiStartHour').value);
      const startM = parseInt(document.getElementById('shamsiStartMin').value);
      const duration = parseInt(document.getElementById('shamsiDuration').value);

      let totalStartMinutes = startH * 60 + startM;
      let totalEndMinutes = totalStartMinutes + duration;
      let endH = Math.floor(totalEndMinutes / 60);
      let endM = totalEndMinutes % 60;

      const fmtH = (h) => (h < 10 ? '0' + h : String(h));
      const fmtM = (m) => (m < 10 ? '0' + m : String(m));

      const slotText = `${fmtH(startH)}:${fmtM(startM)} تا ${fmtH(endH)}:${fmtM(endM)}`;
      selectedShamsiTime = slotText;

      document.querySelectorAll('.shamsi-time-chip').forEach(c => {
        if (c.textContent.trim() === slotText) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });

      updateShamsiSummaryDisplay();
    }

    function toggleCustomDate() {
      const box = document.getElementById('shamsiCustomDateBox');
      const isHidden = box.style.display === 'none';
      box.style.display = isHidden ? 'block' : 'none';
      document.getElementById('customDateToggleText').textContent = isHidden ? 'بستن تنظیمات دلخواه تقویم' : 'انتخاب تاریخ دلخواه دیگر از تقویم شمسی...';
      document.getElementById('customDateToggleIcon').textContent = isHidden ? '▲' : '⚙️';
    }

    function toggleCustomTime() {
      const box = document.getElementById('shamsiCustomTimeBox');
      const isHidden = box.style.display === 'none';
      box.style.display = isHidden ? 'block' : 'none';
      document.getElementById('customTimeToggleText').textContent = isHidden ? 'بستن تنظیمات دلخواه ساعت' : 'تعیین ساعت، دقیقه و مدت مصاحبه به دلخواه...';
      document.getElementById('customTimeToggleIcon').textContent = isHidden ? '▲' : '⏱️';
    }

    function toggleManualInput() {
      const container = document.getElementById('shamsiManualContainer');
      const isHidden = container.style.display === 'none';
      container.style.display = isHidden ? 'block' : 'none';
      if (isHidden) {
        document.getElementById('shamsiManualSlotInput').focus();
      }
    }

    function updateShamsiSummaryDisplay() {
      const dateEl = document.getElementById('shamsiFinalPreviewDate');
      const timeEl = document.getElementById('shamsiFinalPreviewTime');
      const manualInput = document.getElementById('shamsiManualSlotInput');

      if (dateEl) dateEl.textContent = selectedShamsiDate;
      if (timeEl) timeEl.textContent = `ساعت ${selectedShamsiTime} (۲۰ دقیقه - حضوری)`;

      const fullCombined = `${selectedShamsiDate} · ${selectedShamsiTime}`;
      if (manualInput) manualInput.value = fullCombined;
    }

    function openShamsiPicker(cid) {
      initShamsiPickerDom();
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;
      currentShamsiCid = cid;

      document.getElementById('shamsiPickerCid').value = cid;
      document.getElementById('shamsiPickerCandidateSubtitle').textContent = `متقاضی: ${cand.name} (${cand.track} - ${cand.quota || ''})`;

      // Parse current candidate slot if available
      const currentSlot = cand.interview_slot || '';
      if (currentSlot.includes('·')) {
        const parts = currentSlot.split('·');
        selectedShamsiDate = parts[0].trim();
        selectedShamsiTime = parts[1].trim();
      } else if (currentSlot.includes('تا')) {
        selectedShamsiDate = 'سه‌شنبه ۱۹ آبان ۱۴۰۵';
        selectedShamsiTime = currentSlot.trim();
      } else {
        selectedShamsiDate = 'سه‌شنبه ۱۹ آبان ۱۴۰۵';
        selectedShamsiTime = '۰۹:۱۰ تا ۰۹:۳۰';
      }

      // Highlight matching date chip if present
      let matchedDate = false;
      document.querySelectorAll('.shamsi-date-chip').forEach(chip => {
        const numText = chip.querySelector('.shamsi-date-chip-num')?.textContent.trim();
        const dayText = chip.querySelector('.shamsi-date-chip-day')?.textContent.trim();
        if (selectedShamsiDate && ((numText && selectedShamsiDate.includes(numText)) || (dayText && selectedShamsiDate.includes(dayText)))) {
          chip.classList.add('active');
          matchedDate = true;
        } else {
          chip.classList.remove('active');
        }
      });
      if (!matchedDate) {
        const firstChip = document.querySelector('.shamsi-date-chip');
        if (firstChip) firstChip.classList.add('active');
      }

      // Highlight matching time chip if present
      let matchedTime = false;
      document.querySelectorAll('.shamsi-time-chip').forEach(chip => {
        if (chip.textContent.trim() === selectedShamsiTime) {
          chip.classList.add('active');
          matchedTime = true;
        } else {
          chip.classList.remove('active');
        }
      });
      if (!matchedTime) {
        const firstTime = document.querySelector('.shamsi-time-chip');
        if (firstTime) firstTime.classList.add('active');
      }

      updateShamsiSummaryDisplay();

      // Reset collapsible boxes
      document.getElementById('shamsiCustomDateBox').style.display = 'none';
      document.getElementById('customDateToggleText').textContent = 'انتخاب تاریخ دلخواه دیگر از تقویم شمسی...';
      document.getElementById('customDateToggleIcon').textContent = '⚙️';

      document.getElementById('shamsiCustomTimeBox').style.display = 'none';
      document.getElementById('customTimeToggleText').textContent = 'تعیین ساعت، دقیقه و مدت مصاحبه به دلخواه...';
      document.getElementById('customTimeToggleIcon').textContent = '⏱️';

      document.getElementById('shamsiManualContainer').style.display = 'none';

      document.getElementById('shamsiPickerModalOverlay').classList.add('active');
    }

    function closeShamsiPickerModal() {
      document.getElementById('shamsiPickerModalOverlay').classList.remove('active');
      currentShamsiCid = null;
    }

    function handleShamsiOverlayClick(e) {
      if (e.target.id === 'shamsiPickerModalOverlay') closeShamsiPickerModal();
    }

    function saveShamsiTimePicker() {
      const cid = currentShamsiCid;
      const cand = candidates.find(c => c.id === cid);
      if (!cand) return;

      const manualVal = document.getElementById('shamsiManualSlotInput').value.trim();
      const finalSlot = manualVal || `${selectedShamsiDate} · ${selectedShamsiTime}`;

      cand.interview_slot = finalSlot;

      // Update in saved evaluations
      const savedEvals = JSON.parse(localStorage.getItem('admission_evaluations') || '{}');
      if (!savedEvals[String(cid)]) savedEvals[String(cid)] = {};
      savedEvals[String(cid)].interview_slot = finalSlot;
      localStorage.setItem('admission_evaluations', JSON.stringify(savedEvals));

      // Post to backend
      fetch(`/api/candidate/${cid}/eval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_slot: finalSlot })
      }).catch(() => {});

      // If dossier modal is open for this candidate, update evalSlot input as well
      const evalSlotInput = document.getElementById('evalSlot');
      if (evalSlotInput && selectedCandidate && selectedCandidate.id === cid) {
        evalSlotInput.value = finalSlot;
      }

      showToast(`📅 زمان مصاحبه «${cand.name}» با موفقیت ثبت شد: ${finalSlot}`);
      closeShamsiPickerModal();

      renderTimetable();
      renderRoster();
    }

    function openDossierWithSpecificPdf(cid, pdfUrl) {
      openDossierModal(cid, 'pdf');
      setPdfViewer(pdfUrl);
      const pdfSelector = document.getElementById('pdfSelectorBtns');
      if (pdfSelector) {
        pdfSelector.querySelectorAll('.card-btn').forEach(btn => {
          if (btn.getAttribute('onclick')?.includes(pdfUrl)) {
            pdfSelector.querySelectorAll('.card-btn').forEach(b => b.classList.remove('primary'));
            btn.classList.add('primary');
          }
        });
      }
    }

    
    // ==============================================================
    // 1. VISUAL ANALYTICS LOGIC (CHART.JS)
    // ==============================================================
    let chartUnisInstance = null;
    let chartGpaInstance = null;
    let chartQuotaInstance = null;
    let currentQuotaChartView = 'capacity'; // 'capacity' | 'breakdown'

    function switchQuotaChartView(mode) {
      currentQuotaChartView = mode;
      const btnCap = document.getElementById('btnQuotaViewCapacity');
      const btnBrk = document.getElementById('btnQuotaViewBreakdown');
      if (btnCap) btnCap.classList.toggle('active', mode === 'capacity');
      if (btnBrk) btnBrk.classList.toggle('active', mode === 'breakdown');
      renderAnalytics();
    }

    let currentAnalyticsFilter = 'all';
    let quickTrackFilters = { unis: 'all', gpa: 'all' };

    function setAnalyticsFilter(filterKey, btnEl) {
      currentAnalyticsFilter = filterKey;
      document.querySelectorAll('.ana-filter-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) {
        btnEl.classList.add('active');
      } else {
        const matchingBtn = document.querySelector(`.ana-filter-btn[data-filter="${filterKey}"]`);
        if (matchingBtn) matchingBtn.classList.add('active');
      }
      renderAnalytics();
    }

    function setQuickTrackFilter(chartKey, trackKey, btnEl) {
      quickTrackFilters[chartKey] = trackKey;
      if (btnEl && btnEl.parentElement) {
        btnEl.parentElement.querySelectorAll('.chart-tab-btn').forEach(b => b.classList.remove('active'));
        btnEl.classList.add('active');
      }
      renderAnalytics();
    }

    function normalizeUniName(u) {
      if (!u) return 'نامشخص';
      u = u.trim();
      if (u.includes('علم و صنعت')) return 'علم و صنعت ایران';
      if (u.includes('خواجه نصیر')) return 'صنعتی خواجه نصیر';
      if (u.includes('بهشتی')) return 'شهید بهشتی';
      if (u.includes('اصفهان')) return 'صنعتی اصفهان';
      if (u.includes('نوشیروانی') || u.includes('بابل')) return 'نوشیروانی بابل';
      if (u.includes('آزاد')) return 'دانشگاه آزاد';
      if (u.includes('امیرکبیر')) return 'صنعتی امیرکبیر';
      if (u.includes('فردوسی')) return 'فردوسی مشهد';
      if (u.includes('علامه')) return 'علامه طباطبائی';
      if (u.includes('یزد')) return 'دانشگاه یزد';
      if (u.includes('شریف')) return 'صنعتی شریف';
      if (u.includes('بیرجند')) return 'دانشگاه بیرجند';
      if (u.includes('خوارزمی')) return 'دانشگاه خوارزمی';
      if (u.includes('الزهرا')) return 'دانشگاه الزهرا';
      if (u.includes('قم')) return 'دانشگاه قم';
      if (u.includes('گرمسار')) return 'دانشگاه گرمسار';
      if (u.includes('بوئین')) return 'بوئین‌زهرا';
      if (u.includes('مدنی')) return 'شهید مدنی آذربایجان';
      if (u.includes('رازی')) return 'دانشگاه رازی';
      if (u.includes('همدان')) return 'صنعتی همدان';
      if (u.includes('یاسوج')) return 'دانشگاه یاسوج';
      if (u.includes('رجایی')) return 'شهید رجایی تهران';
      if (u.includes('ارومیه')) return 'صنعتی ارومیه';
      return u;
    }

    function getFilteredCandidatesForAnalytics() {
      return rawCandidates.filter(c => {
        if (currentAnalyticsFilter === 'all') return true;
        if (currentAnalyticsFilter === 'ai') return c.track_en === 'AI';
        if (currentAnalyticsFilter === 'sw') return c.track_en === 'Software';
        const q = ((c.quota || '') + ' ' + (c.admission_type || '')).toLowerCase();
        if (currentAnalyticsFilter === 'talented') return q.includes('استعداد');
        if (currentAnalyticsFilter === 'shabaneh') return q.includes('شبانه') || q.includes('نوبت دوم');
        if (currentAnalyticsFilter === 'rozaneh') {
          return !q.includes('استعداد') && !q.includes('شبانه') && !q.includes('نوبت دوم');
        }
        return true;
      });
    }

    function renderAnalytics() {
      // 1. Update filter badges for global counts
      const totalRaw = rawCandidates.length;
      const aiRaw = rawCandidates.filter(c => c.track_en === 'AI').length;
      const swRaw = rawCandidates.filter(c => c.track_en === 'Software').length;
      const talRaw = rawCandidates.filter(c => (c.admission_type || '').includes('استعداد') || (c.quota || '').includes('استعداد')).length;
      const shabRaw = rawCandidates.filter(c => {
        const q = (c.quota || '') + ' ' + (c.admission_type || '');
        return q.includes('شبانه') || q.includes('نوبت دوم');
      }).length;
      const rozRaw = rawCandidates.filter(c => {
        const q = (c.quota || '') + ' ' + (c.admission_type || '');
        return !q.includes('استعداد') && !q.includes('شبانه') && !q.includes('نوبت دوم');
      }).length;

      const anaBadgeAll = document.getElementById('anaBadgeAll');
      if (anaBadgeAll) anaBadgeAll.textContent = totalRaw;
      const anaBadgeAi = document.getElementById('anaBadgeAi');
      if (anaBadgeAi) anaBadgeAi.textContent = aiRaw;
      const anaBadgeSw = document.getElementById('anaBadgeSw');
      if (anaBadgeSw) anaBadgeSw.textContent = swRaw;
      const anaBadgeTal = document.getElementById('anaBadgeTal');
      if (anaBadgeTal) anaBadgeTal.textContent = talRaw;
      const anaBadgeRoz = document.getElementById('anaBadgeRoz');
      if (anaBadgeRoz) anaBadgeRoz.textContent = rozRaw;
      const anaBadgeShab = document.getElementById('anaBadgeShab');
      if (anaBadgeShab) anaBadgeShab.textContent = shabRaw;

      // 2. Filtered candidate set for this analytics view
      const fCands = getFilteredCandidatesForAnalytics();
      const fTotal = fCands.length;
      const fAiCount = fCands.filter(c => c.track_en === 'AI').length;
      const fSwCount = fCands.filter(c => c.track_en === 'Software').length;
      const fTalCount = fCands.filter(c => (c.admission_type || '').includes('استعداد') || (c.quota || '').includes('استعداد')).length;

      let assignedCount = 0;
      fCands.forEach(c => {
        if (seatsState && Object.values(seatsState).includes(c.id)) {
          assignedCount++;
        }
      });

      let gpaSum = 0;
      let gpaNumCount = 0;
      fCands.forEach(c => {
        const val = parseFloat(c.gpa_val || c.bsc_gpa);
        if (!isNaN(val) && val > 0) {
          gpaSum += val;
          gpaNumCount++;
        }
      });
      const avgGpa = gpaNumCount > 0 ? (gpaSum / gpaNumCount).toFixed(2) : '-';

      // Update KPI counters
      const statTotalEl = document.getElementById('statTotalCands');
      if (statTotalEl) statTotalEl.textContent = fTotal;
      const statAiEl = document.getElementById('statAiCands');
      if (statAiEl) statAiEl.textContent = fAiCount;
      const statSwEl = document.getElementById('statSwCands');
      if (statSwEl) statSwEl.textContent = fSwCount;
      const statTalEl = document.getElementById('statTalCands');
      if (statTalEl) statTalEl.textContent = fTalCount;
      const statSeatsEl = document.getElementById('statAssignedSeats');
      if (statSeatsEl) statSeatsEl.textContent = `${assignedCount} / ${SEATS_CONFIG.length}`;
      const statGpaEl = document.getElementById('statAvgGpa');
      if (statGpaEl) statGpaEl.textContent = avgGpa;

      const statAiSub = document.getElementById('statAiSub');
      if (statAiSub) statAiSub.textContent = fTotal > 0 ? `${((fAiCount / fTotal) * 100).toFixed(1)}٪ جامعه آماری` : '-';
      const statSwSub = document.getElementById('statSwSub');
      if (statSwSub) statSwSub.textContent = fTotal > 0 ? `${((fSwCount / fTotal) * 100).toFixed(1)}٪ جامعه آماری` : '-';

      if (typeof Chart === 'undefined') {
        console.warn('Chart.js not yet loaded');
        return;
      }

      // -------------------------------------------------------------
      // Chart 1: Universities Distribution (Filterable & Stacked)
      // -------------------------------------------------------------
      let uniCands = fCands;
      if (quickTrackFilters.unis === 'AI') {
        uniCands = uniCands.filter(c => c.track_en === 'AI');
      } else if (quickTrackFilters.unis === 'Software') {
        uniCands = uniCands.filter(c => c.track_en === 'Software');
      }

      const uniMap = {};
      uniCands.forEach(c => {
        const u = normalizeUniName(c.bsc_uni);
        if (!uniMap[u]) {
          uniMap[u] = { ai: [], sw: [], total: 0 };
        }
        const candInfo = { id: c.id, name: c.name, gpa: c.gpa_val || c.bsc_gpa || '-' };
        if (c.track_en === 'AI') {
          uniMap[u].ai.push(candInfo);
        } else {
          uniMap[u].sw.push(candInfo);
        }
        uniMap[u].total++;
      });

      const sortedUnis = Object.keys(uniMap).sort((a, b) => uniMap[b].total - uniMap[a].total);
      const uniLabels = sortedUnis;

      const showStackedUnis = (quickTrackFilters.unis === 'all');
      let uniDatasets = [];

      if (showStackedUnis) {
        uniDatasets = [
          {
            label: 'گرایش هوش مصنوعی',
            data: sortedUnis.map(u => uniMap[u].ai.length),
            backgroundColor: '#0E7C86',
            borderColor: '#1A1915',
            borderWidth: 1.5,
            borderRadius: 3,
            stack: 'uniStack'
          },
          {
            label: 'نرم‌افزار',
            data: sortedUnis.map(u => uniMap[u].sw.length),
            backgroundColor: '#C0392B',
            borderColor: '#1A1915',
            borderWidth: 1.5,
            borderRadius: 3,
            stack: 'uniStack'
          }
        ];
      } else if (quickTrackFilters.unis === 'AI') {
        uniDatasets = [{
          label: 'گرایش هوش مصنوعی',
          data: sortedUnis.map(u => uniMap[u].ai.length),
          backgroundColor: '#0E7C86',
          borderColor: '#1A1915',
          borderWidth: 1.5,
          borderRadius: 3
        }];
      } else {
        uniDatasets = [{
          label: 'نرم‌افزار',
          data: sortedUnis.map(u => uniMap[u].sw.length),
          backgroundColor: '#C0392B',
          borderColor: '#1A1915',
          borderWidth: 1.5,
          borderRadius: 3
        }];
      }

      const ctxUnis = document.getElementById('chartUnisCanvas')?.getContext('2d');
      if (ctxUnis) {
        if (chartUnisInstance) chartUnisInstance.destroy();
        chartUnisInstance = new Chart(ctxUnis, {
          type: 'bar',
          data: {
            labels: uniLabels,
            datasets: uniDatasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
              legend: {
                display: showStackedUnis,
                position: 'top',
                labels: { font: { family: 'Vazirmatn', size: 11, weight: 'bold' } }
              },
              tooltip: {
                rtl: true,
                textDirection: 'rtl',
                callbacks: {
                  title: function(items) {
                    return '🏛️ دانشگاه: ' + items[0].label;
                  },
                  afterBody: function(items) {
                    const u = items[0].label;
                    const entry = uniMap[u];
                    if (!entry) return [];
                    const lines = [];
                    if (entry.ai.length > 0 && (showStackedUnis || quickTrackFilters.unis === 'AI')) {
                      const aiNames = entry.ai.map(x => `${x.name} (${x.gpa})`).join('، ');
                      lines.push(`🤖 هوش (${entry.ai.length} نفر): ${aiNames}`);
                    }
                    if (entry.sw.length > 0 && (showStackedUnis || quickTrackFilters.unis === 'Software')) {
                      const swNames = entry.sw.map(x => `${x.name} (${x.gpa})`).join('، ');
                      lines.push(`💻 نرم‌افزار (${entry.sw.length} نفر): ${swNames}`);
                    }
                    return lines;
                  },
                  footer: function(items) {
                    const u = items[0].label;
                    const entry = uniMap[u];
                    return entry ? `مجموع در این دانشگاه: ${entry.total} نفر` : '';
                  }
                }
              }
            },
            scales: {
              x: {
                stacked: showStackedUnis,
                ticks: {
                  font: { family: 'Vazirmatn', size: 10, weight: '600' },
                  autoSkip: false,
                  maxRotation: 45,
                  minRotation: 25
                }
              },
              y: {
                stacked: showStackedUnis,
                beginAtZero: true,
                ticks: { stepSize: 1, font: { family: 'Vazirmatn' } }
              }
            }
          }
        });
      }

      // -------------------------------------------------------------
      // Chart 2: Detailed GPA Histogram (0.5 Step Granularity)
      // -------------------------------------------------------------
      let gpaCands = fCands;
      if (quickTrackFilters.gpa === 'AI') {
        gpaCands = gpaCands.filter(c => c.track_en === 'AI');
      } else if (quickTrackFilters.gpa === 'Software') {
        gpaCands = gpaCands.filter(c => c.track_en === 'Software');
      }

      const GPA_BINS = [
        { id: 'b0', label: '< ۱۶.۰۰', min: 0.0, max: 16.0 },
        { id: 'b1', label: '۱۶.۰۰ - ۱۶.۴۹', min: 16.0, max: 16.5 },
        { id: 'b2', label: '۱۶.۵۰ - ۱۶.۹۹', min: 16.5, max: 17.0 },
        { id: 'b3', label: '۱۷.۰۰ - ۱۷.۴۹', min: 17.0, max: 17.5 },
        { id: 'b4', label: '۱۷.۵۰ - ۱۷.۹۹', min: 17.5, max: 18.0 },
        { id: 'b5', label: '۱۸.۰۰ - ۱۸.۴۹', min: 18.0, max: 18.5 },
        { id: 'b6', label: '۱۸.۵۰ - ۱۸.۹۹', min: 18.5, max: 19.0 },
        { id: 'b7', label: '۱۹.۰۰ - ۱۹.۴۹', min: 19.0, max: 19.5 },
        { id: 'b8', label: '۱۹.۵۰ - ۲۰.۰۰', min: 19.5, max: 20.01 }
      ];

      const binData = {};
      GPA_BINS.forEach(b => {
        binData[b.id] = { ai: [], sw: [], total: 0 };
      });

      const validGpaList = [];
      let unstatedGpaCount = 0;

      gpaCands.forEach(c => {
        let val = parseFloat(c.gpa_val || c.bsc_gpa);
        if (isNaN(val) || val <= 0) {
          unstatedGpaCount++;
          return;
        }
        validGpaList.push({ name: c.name, track: c.track_en, val: val });

        for (let i = 0; i < GPA_BINS.length; i++) {
          const b = GPA_BINS[i];
          if (val >= b.min && val < b.max) {
            if (c.track_en === 'AI') {
              binData[b.id].ai.push({ name: c.name, gpa: val });
            } else {
              binData[b.id].sw.push({ name: c.name, gpa: val });
            }
            binData[b.id].total++;
            break;
          }
        }
      });

      // Update Detailed GPA Stats Pill
      validGpaList.sort((a, b) => a.val - b.val);
      const pillEl = document.getElementById('gpaDetailedStatsPill');
      if (pillEl) {
        if (validGpaList.length > 0) {
          const minObj = validGpaList[0];
          const maxObj = validGpaList[validGpaList.length - 1];
          const sumVal = validGpaList.reduce((acc, curr) => acc + curr.val, 0);
          const meanVal = (sumVal / validGpaList.length).toFixed(2);

          const mid = Math.floor(validGpaList.length / 2);
          const medianVal = (validGpaList.length % 2 !== 0) 
            ? validGpaList[mid].val.toFixed(2)
            : ((validGpaList[mid - 1].val + validGpaList[mid].val) / 2).toFixed(2);

          const aCount = validGpaList.filter(x => x.val >= 17.5).length;
          const aPct = Math.round((aCount / validGpaList.length) * 100);

          let pillHtml = `
            <div class="gpa-stat-item"><span>👥 تعداد دارای معدل:</span> <span class="val">${validGpaList.length} نفر</span></div>
            <div class="gpa-stat-item"><span>🎓 میانگین:</span> <span class="val">${meanVal}</span></div>
            <div class="gpa-stat-item"><span>⚖️ میانه:</span> <span class="val">${medianVal}</span></div>
            <div class="gpa-stat-item"><span>⭐ بالاترین:</span> <span class="val">${maxObj.val} (${maxObj.name})</span></div>
            <div class="gpa-stat-item"><span>🔻 پایین‌ترین:</span> <span class="val">${minObj.val} (${minObj.name})</span></div>
            <div class="gpa-stat-item"><span>✨ رتبه الف (≥۱۷.۵):</span> <span class="val">${aCount} نفر (${aPct}٪)</span></div>
          `;
          if (unstatedGpaCount > 0) {
            pillHtml += `<div class="gpa-stat-item" style="color:var(--color-ink-muted);"><span>ℹ️ بدون معدل در پرونده:</span> <span class="val">${unstatedGpaCount} نفر</span></div>`;
          }
          pillEl.innerHTML = pillHtml;
        } else {
          pillEl.innerHTML = `<div style="color:var(--color-ink-muted); text-align:center; width:100%;">داده‌ای برای این فیلتر ثبت نشده است.</div>`;
        }
      }

      const showStackedGpa = (quickTrackFilters.gpa === 'all');
      let gpaDatasets = [];

      if (showStackedGpa) {
        gpaDatasets = [
          {
            label: 'گرایش هوش مصنوعی',
            data: GPA_BINS.map(b => binData[b.id].ai.length),
            backgroundColor: '#0E7C86',
            borderColor: '#1A1915',
            borderWidth: 1.5,
            borderRadius: 3,
            stack: 'gpaStack'
          },
          {
            label: 'نرم‌افزار',
            data: GPA_BINS.map(b => binData[b.id].sw.length),
            backgroundColor: '#C0392B',
            borderColor: '#1A1915',
            borderWidth: 1.5,
            borderRadius: 3,
            stack: 'gpaStack'
          }
        ];
      } else if (quickTrackFilters.gpa === 'AI') {
        gpaDatasets = [{
          label: 'گرایش هوش مصنوعی',
          data: GPA_BINS.map(b => binData[b.id].ai.length),
          backgroundColor: '#0E7C86',
          borderColor: '#1A1915',
          borderWidth: 1.5,
          borderRadius: 3
        }];
      } else {
        gpaDatasets = [{
          label: 'نرم‌افزار',
          data: GPA_BINS.map(b => binData[b.id].sw.length),
          backgroundColor: '#C0392B',
          borderColor: '#1A1915',
          borderWidth: 1.5,
          borderRadius: 3
        }];
      }

      const ctxGpa = document.getElementById('chartGpaCanvas')?.getContext('2d');
      if (ctxGpa) {
        if (chartGpaInstance) chartGpaInstance.destroy();
        chartGpaInstance = new Chart(ctxGpa, {
          type: 'bar',
          data: {
            labels: GPA_BINS.map(b => b.label),
            datasets: gpaDatasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
              legend: {
                display: showStackedGpa,
                position: 'top',
                labels: { font: { family: 'Vazirmatn', size: 11, weight: 'bold' } }
              },
              tooltip: {
                rtl: true,
                textDirection: 'rtl',
                callbacks: {
                  title: function(items) {
                    return 'بازه نمره معدل: ' + items[0].label;
                  },
                  afterBody: function(items) {
                    const binIdx = items[0].dataIndex;
                    const b = GPA_BINS[binIdx];
                    const entry = binData[b.id];
                    const lines = [];
                    if (entry.ai.length > 0 && (showStackedGpa || quickTrackFilters.gpa === 'AI')) {
                      const aiList = entry.ai.map(x => `${x.name} (${x.gpa})`).join('، ');
                      lines.push(`🤖 هوش (${entry.ai.length} نفر): ${aiList}`);
                    }
                    if (entry.sw.length > 0 && (showStackedGpa || quickTrackFilters.gpa === 'Software')) {
                      const swList = entry.sw.map(x => `${x.name} (${x.gpa})`).join('، ');
                      lines.push(`💻 نرم‌افزار (${entry.sw.length} نفر): ${swList}`);
                    }
                    return lines;
                  },
                  footer: function(items) {
                    const binIdx = items[0].dataIndex;
                    const b = GPA_BINS[binIdx];
                    const entry = binData[b.id];
                    return `مجموع این بازه: ${entry.total} نفر`;
                  }
                }
              }
            },
            scales: {
              x: {
                stacked: showStackedGpa,
                ticks: { font: { family: 'Vazirmatn', size: 10.5, weight: '600' } }
              },
              y: {
                stacked: showStackedGpa,
                beginAtZero: true,
                ticks: { stepSize: 1, font: { family: 'Vazirmatn' } }
              }
            }
          }
        });
      }

      // -------------------------------------------------------------
      // Chart 3: Detailed Quotas & Capacity Admission Analysis
      // -------------------------------------------------------------
      const swRozAssigned = SEATS_CONFIG.filter(s => s.group === 'sw_roz' && seatsState[s.id] !== null).length;
      const aiRozAssigned = SEATS_CONFIG.filter(s => s.group === 'ai_roz' && seatsState[s.id] !== null).length;
      const aiShabAssigned = SEATS_CONFIG.filter(s => s.group === 'ai_shab' && seatsState[s.id] !== null).length;

      // Calculate applicant pool from fCands
      const swCandidates = fCands.filter(c => c.track_en === 'Software' || (c.track && c.track.includes('نرم‌افزار')));
      const swTotal = swCandidates.length;
      const swPhase1 = swCandidates.filter(c => c.interview_phase === 'phase1').length;
      const swTal = swCandidates.filter(c => (c.admission_type || '').includes('استعداد') || (c.quota || '').includes('استعداد')).length;
      const swRoz = swTotal - swTal;

      const aiRozCandidates = fCands.filter(c => (c.track_en === 'AI' || (c.track && c.track.includes('هوش'))) && !((c.admission_type || '').includes('شبانه') || (c.quota || '').includes('شبانه')));
      const aiRozTotal = aiRozCandidates.length;
      const aiRozPhase1 = aiRozCandidates.filter(c => c.interview_phase === 'phase1').length;
      const aiTal = aiRozCandidates.filter(c => (c.admission_type || '').includes('استعداد') || (c.quota || '').includes('استعداد')).length;
      const aiRoz = aiRozTotal - aiTal;

      const aiShabCandidates = fCands.filter(c => (c.track_en === 'AI' || (c.track && c.track.includes('هوش'))) && ((c.admission_type || '').includes('شبانه') || (c.quota || '').includes('شبانه')));
      const aiShabTotal = aiShabCandidates.length;
      const aiShabPhase1 = aiShabCandidates.filter(c => c.interview_phase === 'phase1').length;
      const aiShab = aiShabTotal;

      // Update Summary Strip Numbers
      const elSet = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
      elSet('stripSwRozAssigned', swRozAssigned);
      elSet('stripSwRozPhase1', swPhase1);
      elSet('stripAiRozAssigned', aiRozAssigned);
      elSet('stripAiRozPhase1', aiRozPhase1);
      elSet('stripAiShabAssigned', aiShabAssigned);
      elSet('stripAiShabPhase1', aiShabPhase1);

      const ctxQuota = document.getElementById('chartQuotaCanvas')?.getContext('2d');
      if (ctxQuota) {
        if (chartQuotaInstance) chartQuotaInstance.destroy();

        if (currentQuotaChartView === 'capacity') {
          // GROUPED BAR: Capacity vs Accepted vs Phase 1 vs Total Applicants
          chartQuotaInstance = new Chart(ctxQuota, {
            type: 'bar',
            data: {
              labels: [
                '💻 روزانه نرم‌افزار (۴ سهمیه مصوب)',
                '🤖 روزانه هوش مصنوعی (۲ سهمیه مصوب)',
                '🌙 شبانه هوش مصنوعی (۲ سهمیه مصوب)'
              ],
              datasets: [
                {
                  label: '🏛️ سقف ظرفیت مصوب آزمایشگاه',
                  data: [4, 2, 2],
                  backgroundColor: '#1E293B',
                  borderColor: '#0F172A',
                  borderWidth: 1.5,
                  borderRadius: 4,
                  barPercentage: 0.8,
                  categoryPercentage: 0.8
                },
                {
                  label: '✅ پذیرفته‌شدگان قطعی در سامانه',
                  data: [swRozAssigned, aiRozAssigned, aiShabAssigned],
                  backgroundColor: '#059669',
                  borderColor: '#047857',
                  borderWidth: 1.5,
                  borderRadius: 4,
                  barPercentage: 0.8,
                  categoryPercentage: 0.8
                },
                {
                  label: '🟣 متقاضیان فاز ۱ (اولویت اول مصاحبه)',
                  data: [swPhase1, aiRozPhase1, aiShabPhase1],
                  backgroundColor: '#7C3AED',
                  borderColor: '#6D28D9',
                  borderWidth: 1.5,
                  borderRadius: 4,
                  barPercentage: 0.8,
                  categoryPercentage: 0.8
                },
                {
                  label: '👥 کل متقاضیان پرونده‌ها',
                  data: [swTotal, aiRozTotal, aiShabTotal],
                  backgroundColor: '#0284C7',
                  borderColor: '#0369A1',
                  borderWidth: 1.5,
                  borderRadius: 4,
                  barPercentage: 0.8,
                  categoryPercentage: 0.8
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top',
                  labels: {
                    font: { family: 'Vazirmatn', size: 12, weight: '700' },
                    padding: 14,
                    usePointStyle: true
                  }
                },
                tooltip: {
                  titleFont: { family: 'Vazirmatn', size: 13, weight: 'bold' },
                  bodyFont: { family: 'Vazirmatn', size: 12 },
                  padding: 12,
                  boxPadding: 6,
                  callbacks: {
                    label: function(ctx) {
                      return ` ${ctx.dataset.label}: ${ctx.raw} نفر`;
                    }
                  }
                }
              },
              scales: {
                x: {
                  grid: { display: false },
                  ticks: { font: { family: 'Vazirmatn', size: 12, weight: '700' } }
                },
                y: {
                  beginAtZero: true,
                  grid: { color: 'rgba(0, 0, 0, 0.06)' },
                  ticks: { font: { family: 'Vazirmatn', size: 11 }, stepSize: 2 }
                }
              }
            }
          });
        } else {
          // STACKED BAR: Breakdown of Quotas by Track
          chartQuotaInstance = new Chart(ctxQuota, {
            type: 'bar',
            data: {
              labels: [
                `💻 گرایش مهندسی نرم‌افزار (${swTotal} متقاضی)`,
                `🤖 گرایش هوش مصنوعی (${aiRozTotal + aiShabTotal} متقاضی)`
              ],
              datasets: [
                {
                  label: '🎓 آزمون سراسری (روزانه)',
                  data: [swRoz, aiRoz],
                  backgroundColor: '#0284C7',
                  borderColor: '#0369A1',
                  borderWidth: 1.5,
                  borderRadius: 4
                },
                {
                  label: '🏆 سهمیه استعدادهای درخشان',
                  data: [swTal, aiTal],
                  backgroundColor: '#D97706',
                  borderColor: '#B45309',
                  borderWidth: 1.5,
                  borderRadius: 4
                },
                {
                  label: '🌙 نوبت دوم (شبانه)',
                  data: [0, aiShab],
                  backgroundColor: '#7C3AED',
                  borderColor: '#6D28D9',
                  borderWidth: 1.5,
                  borderRadius: 4
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top',
                  labels: {
                    font: { family: 'Vazirmatn', size: 12, weight: '700' },
                    padding: 14,
                    usePointStyle: true
                  }
                },
                tooltip: {
                  titleFont: { family: 'Vazirmatn', size: 13, weight: 'bold' },
                  bodyFont: { family: 'Vazirmatn', size: 12 },
                  padding: 12,
                  boxPadding: 6,
                  callbacks: {
                    label: function(ctx) {
                      return ` ${ctx.dataset.label}: ${ctx.raw} نفر`;
                    }
                  }
                }
              },
              scales: {
                x: {
                  stacked: true,
                  grid: { display: false },
                  ticks: { font: { family: 'Vazirmatn', size: 12, weight: '700' } }
                },
                y: {
                  stacked: true,
                  beginAtZero: true,
                  grid: { color: 'rgba(0, 0, 0, 0.06)' },
                  ticks: { font: { family: 'Vazirmatn', size: 11 }, stepSize: 5 }
                }
              }
            }
          });
        }
      }
    }

    // ==============================================================
    // 3. EMAIL TEMPLATE GENERATOR LOGIC
    // ==============================================================
    let currentEmailCandidate = null;
    let currentEmailTemplateKey = 'interview';

    function openEmailModal(cid, templateKey = 'interview') {
      const cand = candidates.find(c => c.id === parseInt(cid));
      if (!cand) return;
      currentEmailCandidate = cand;

      document.getElementById('emailModalCandidateSubtitle').textContent = 
        `متقاضی: ${cand.name} | گرایش ${cand.track} | دوره ${cand.admission_type}`;
      document.getElementById('emailModalTo').value = cand.email || '';

      applyEmailTemplate(templateKey);
      document.getElementById('emailTemplateModalOverlay').classList.add('active');
    }

    function closeEmailModal() {
      document.getElementById('emailTemplateModalOverlay').classList.remove('active');
    }

    function handleEmailModalOverlayClick(e) {
      if (e.target.id === 'emailTemplateModalOverlay') closeEmailModal();
    }

    function selectEmailTemplate(templateKey, btn) {
      document.querySelectorAll('.email-tpl-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      applyEmailTemplate(templateKey);
    }

    function applyEmailTemplate(templateKey) {
      currentEmailTemplateKey = templateKey;
      if (!currentEmailCandidate) return;
      const c = currentEmailCandidate;
      const slot = c.interview_slot || 'تاریخ و ساعت مصاحبه متعاقباً اعلام خواهد شد';
      const assignedSeat = getCandidateAssignedSeat(c.id);
      const seatTitle = assignedSeat ? assignedSeat.title : `گرایش ${c.track}`;

      const tplVars = {
        name: c.name || '',
        track: c.track || '',
        slot: slot,
        location: CONFIG.interview_location_default || 'اتاق آزمایشگاه / دفتر استاد راهنما',
        map_url: CONFIG.interview_map_url || '',
        supervisor_name: CONFIG.supervisor_name || 'استاد راهنما',
        lab_name: CONFIG.lab_name || 'آزمایشگاه',
        lab_short: CONFIG.lab_short || 'LAB',
        institution: CONFIG.institution || 'دانشگاه',
        academic_year: CONFIG.academic_year || '۱۴۰۵ - ۱۴۰۶',
        seat_title: seatTitle
      };

      function formatTpl(str) {
        if (!str) return '';
        return str.replace(/\{(\w+)\}/g, (match, key) => {
          return tplVars[key] !== undefined ? tplVars[key] : match;
        });
      }

      let subject = '';
      let body = '';

      const tpls = CONFIG.email_templates || {};

      if (templateKey === 'interview') {
        if (tpls.invitation) {
          subject = formatTpl(tpls.invitation.subject);
          body = formatTpl(tpls.invitation.body);
        } else {
          subject = `دعوت به مصاحبه حضوری پذیرش کارشناسی ارشد ${tplVars.academic_year} - ${tplVars.lab_name} - ${c.name}`;
          body = `جناب آقای / سرکار خانم ${c.name} گرامی،\nبا سلام و احترام،\n\nپیرو بررسی سوابق علمی ارزشمند ارسالی جنابعالی برای دوره کارشناسی ارشد گرایش ${c.track}، بدین‌وسیله از شما جهت شرکت در جلسه مصاحبه حضوری و ارزیابی تخصصی در ${tplVars.lab_name} (${tplVars.institution}) دعوت به عمل می‌آید.\n\n📅 زمان جلسه مصاحبه شما:\nروز و ساعت: ${slot} (به صورت حضوری)\n\n📍 محل مصاحبه:\n${tplVars.location}\n\n📌 نکات مهم:\n۱. لطفاً حداقل ۱۰ دقیقه پیش از ساعت اعلام‌شده در محل حضور داشته باشید.\n۲. در صورت تمایل، نمونه کارها یا لپ‌تاپ شخصی خود را جهت ارائه همراه داشته باشید.\n\nبا آرزوی موفقیت،\n${tplVars.supervisor_name}\n${tplVars.lab_name} - ${tplVars.institution}`;
        }
      } else if (templateKey === 'simple_interview') {
        subject = `جلسه مصاحبه حضوری - ${c.name}`;
        body = `سلام،\nوقت بخیر\n\nشما برای انجام جلسه مصاحبه حضوری انتخاب شدید.\nزمان و روز جلسه: ${slot}\n\nمکان برگزاری جلسه:\n${tplVars.location}\n${tplVars.map_url}`;
      } else if (templateKey === 'accepted') {
        if (tpls.acceptance) {
          subject = formatTpl(tpls.acceptance.subject);
          body = formatTpl(tpls.acceptance.body);
        } else {
          subject = `اعلام پذیرش قطعی در ${tplVars.lab_name} - کارشناسی ارشد ${tplVars.academic_year} - ${c.name}`;
          body = `جناب آقای / سرکار خانم ${c.name} گرامی،\nبا سلام و احترام،\n\nضمن ابراز خرسندی، به اطلاع می‌رساند با توجه به سوابق درخشان تحصیلی و ارزیابی مصاحبه تخصصی، جنابعالی به عنوان دانشجوی کارشناسی ارشد در ${seatTitle} در ${tplVars.lab_name} تحت راهنمایی ${tplVars.supervisor_name} پذیرفته شده‌اید.\n\nتخصیص ظرفیت شما در سامانه آزمایشگاه تایید نهایی گردید.\n\nبا احترام فراوان،\n${tplVars.supervisor_name}\n${tplVars.lab_name} - ${tplVars.institution}`;
        }
      } else if (templateKey === 'waitlist') {
        if (tpls.waitlist) {
          subject = formatTpl(tpls.waitlist.subject);
          body = formatTpl(tpls.waitlist.body);
        } else {
          subject = `اطلاع‌رسانی وضعیت ارزیابی و لیست انتظار - ${tplVars.lab_name} - ${c.name}`;
          body = `جناب آقای / سرکار خانم ${c.name} گرامی،\nبا سلام و احترام،\n\nضمن تشکر از حضور ارزشمند شما در فرایند پذیرش، پرونده شما در حال حاضر به دلیل سقف محدود ظرفیت در «لیست انتظار» قرار گرفته است.\n\nبا آرزوی توفیق،\n${tplVars.lab_name} - ${tplVars.institution}`;
        }
      } else if (templateKey === 'rejected') {
        if (tpls.rejection) {
          subject = formatTpl(tpls.rejection.subject);
          body = formatTpl(tpls.rejection.body);
        } else {
          subject = `نتیجه بررسی فرایند پذیرش کارشناسی ارشد ${tplVars.academic_year} - ${tplVars.lab_name}`;
          body = `جناب آقای / سرکار خانم ${c.name} گرامی،\nبا سلام و احترام،\n\nضمن قدردانی از ارسال رزومه و سوابق تحصیلی ارزشمند شما، متاسفانه به دلیل محدودیت شدید ظرفیت امکان پذیرش شما در این دوره فراهم نگردید.\nبرای شما آرزوی موفقیت و توفیق روزافزون داریم.\n\nبا احترام،\n${tplVars.lab_name} - ${tplVars.institution}`;
        }
      } else if (templateKey === 'docs') {
        subject = `درخواست ارسال مستندات و کارنامه تکمیلی - ${tplVars.lab_name} - ${c.name}`;
        body = `جناب آقای / سرکار خانم ${c.name} گرامی،\nبا سلام و احترام،\n\nجهت تکمیل فرایند ارزیابی پرونده شما در ${tplVars.lab_name} (${tplVars.institution})، خواهشمند است مدارک تکمیلی زیر را در پاسخ به همین ایمیل ارسال فرمایید:\n\n۱. فایل PDF کارنامه ریزنمرات تفصیلی کارشناسی (شامل معدل تا ترم جاری)\n۲. لینک ریپازیتوری گیت‌هاب پروژه‌های شاخص یا مقالات (در صورت وجود)\n۳. توضیحات مختصر در خصوص زمینه‌های پژوهشی مورد علاقه شما\n\nبا احترام،\n${tplVars.lab_name} - ${tplVars.institution}`;
      }

      document.getElementById('emailModalSubject').value = subject;
      document.getElementById('emailModalBody').value = body.replace(/\\n/g, '\n');
    }

    function copyEmailBody() {
      const body = document.getElementById('emailModalBody').value;
      copyContactText(body);
      showToast('📋 متن پیام ایمیل با موفقیت کپی شد');
    }

    function copyEmailSubject() {
      const subj = document.getElementById('emailModalSubject').value;
      copyContactText(subj);
      showToast('📋 موضوع ایمیل با موفقیت کپی شد');
    }

    function openMailto() {
      const to = document.getElementById('emailModalTo').value;
      const subj = document.getElementById('emailModalSubject').value;
      const body = document.getElementById('emailModalBody').value;
      const url = `mailto:${encodeURIComponent(to)}?subject=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`;
      window.open(url, '_blank');
    }

    function openGmailWeb() {
      const to = document.getElementById('emailModalTo').value;
      const subj = document.getElementById('emailModalSubject').value;
      const body = document.getElementById('emailModalBody').value;
      const url = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(to)}&su=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`;
      window.open(url, '_blank');
    }

    
    // ==========================================
    // EXPORT STUDIO LOGIC & ADVANCED REPORTING
    // ==========================================
    const EXPORT_COLUMNS = [
      { id: 'idx', label: 'ردیف', default: true, getValue: (c, i) => i + 1 },
      { id: 'name', label: 'نام و نام خانوادگی', default: true, getValue: (c) => c.name },
      { id: 'phase', label: 'فاز مصاحبه', default: true, getValue: (c) => getPhaseLabel(c.interview_phase) },
      { id: 'track', label: 'گرایش ارشد', default: true, getValue: (c) => c.track },
      { id: 'admission', label: 'نوع قبولی و سهمیه', default: true, getValue: (c) => c.quota || c.admission_type },
      { id: 'rank_arshad', label: 'رتبه ارشد', default: true, getValue: (c) => c.konkur_arshad },
      { id: 'bsc_uni', label: 'دانشگاه کارشناسی', default: true, getValue: (c) => c.bsc_uni },
      { id: 'bsc_major', label: 'رشته کارشناسی', default: false, getValue: (c) => c.bsc_major },
      { id: 'bsc_gpa', label: 'معدل کارشناسی', default: true, getValue: (c) => c.bsc_gpa },
      { id: 'konkur_bsc', label: 'رتبه کارشناسی', default: false, getValue: (c) => c.konkur_bsc || '-' },
      { id: 'high_school', label: 'دبیرستان / سمپاد', default: false, getValue: (c) => c.high_school },
      { id: 'interview_slot', label: 'ساعت مصاحبه (حضوری)', default: true, getValue: (c) => c.interview_slot || '-' },
      { id: 'status', label: 'وضعیت پذیرش', default: true, getValue: (c) => {
          const seat = getCandidateAssignedSeat(c.id);
          if (seat) return `✅ قبولی (${seat.title.split(':')[1]?.trim() || seat.title})`;
          if (c.status === 'دعوت به مصاحبه') return '📅 دعوت به مصاحبه';
          if (c.status === 'رد شده' || c.status === 'عدم پذیرش') return `❌ رد شده${c.eval_notes ? ' (' + c.eval_notes + ')' : ''}`;
          return '⏳ در انتظار بررسی';
        }
      },
      { id: 'seat', label: 'ظرفیت آزمایشگاه', default: false, getValue: (c) => {
          const seat = getCandidateAssignedSeat(c.id);
          return seat ? seat.title : 'بدون صندلی';
        }
      },
      { id: 'score', label: 'نمره ارزیابی (از ۱۰۰)', default: false, getValue: (c) => c.score ? `${c.score}` : 'ثبت نشده' },
      { id: 'phone', label: 'شماره همراه', default: true, getValue: (c) => c.phone || '-' },
      { id: 'email', label: 'آدرس ایمیل', default: true, getValue: (c) => c.email || '-' },
      { id: 'social', label: 'لینک‌ها و شبکه‌ها', default: false, getValue: (c) => c.social || '-' },
      { id: 'skills', label: 'مهارت‌های تخصصی', default: false, getValue: (c) => c.skills || '-' },
      { id: 'exp', label: 'سوابق و پروژه‌ها', default: false, getValue: (c) => c.exp || '-' },
      { id: 'interests', label: 'علایق و پایان‌نامه', default: false, getValue: (c) => c.interests || '-' },
      { id: 'eval_notes', label: 'یادداشت‌های مصاحبه', default: false, getValue: (c) => c.eval_notes || '-' }
    ];

    let exportFilters = {
      track: 'all',
      phase: 'all',
      admission: 'all',
      status: 'all',
      interviewDate: 'all',
      minGpa: 0,
      rank: 'all',
      uni: 'all',
      starred: 'all',
      query: ''
    };

    let selectedExportColumns = new Set(EXPORT_COLUMNS.filter(c => c.default).map(c => c.id));

    function initExportStudio() {
      populateInterviewDateFilter();
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function populateInterviewDateFilter() {
      const sel = document.getElementById('expFilterInterviewDate');
      if (!sel) return;
      const currentVal = sel.value || exportFilters.interviewDate || 'all';

      // Gather distinct dates from candidates
      const dateMap = new Map(); // dateString -> count
      candidates.forEach(c => {
        const slot = (c.interview_slot || '').trim();
        if (slot) {
          const datePart = slot.split('·')[0].trim();
          if (datePart) {
            dateMap.set(datePart, (dateMap.get(datePart) || 0) + 1);
          }
        }
      });

      let html = '<option value="all">همه روزها و تاریخ‌های مصاحبه</option>';
      const totalScheduled = candidates.filter(c => c.interview_slot && c.interview_slot.trim()).length;
      html += `<option value="has_date">📋 کلیه مصاحبه‌شوندگان (${totalScheduled} نفر)</option>`;

      // Sort dates
      const sortedDates = Array.from(dateMap.keys()).sort();
      sortedDates.forEach(d => {
        const count = dateMap.get(d);
        html += `<option value="${d}">🗓️ ${d} (${count} داوطلب)</option>`;
      });

      const noDateCount = candidates.length - totalScheduled;
      html += `<option value="no_date">⚪ بدون تاریخ مصاحبه (${noDateCount} نفر)</option>`;

      sel.innerHTML = html;
      if (currentVal && Array.from(sel.options).some(o => o.value === currentVal)) {
        sel.value = currentVal;
      }
    }

    function renderColumnCheckboxes() {
      const container = document.getElementById('exportColumnsContainer');
      if (!container) return;
      container.innerHTML = '';

      EXPORT_COLUMNS.forEach(col => {
        const isChecked = selectedExportColumns.has(col.id);
        const label = document.createElement('label');
        label.className = `column-check-item ${isChecked ? 'active' : ''}`;
        label.innerHTML = `
          <input type="checkbox" value="${col.id}" ${isChecked ? 'checked' : ''} onchange="toggleExportColumn('${col.id}', this)">
          <span>${col.label}</span>
        `;
        container.appendChild(label);
      });

      const badge = document.getElementById('colCountBadge');
      if (badge) badge.textContent = `${selectedExportColumns.size} ستون فعال`;
    }

    function toggleExportColumn(colId, chk) {
      if (chk.checked) {
        selectedExportColumns.add(colId);
      } else {
        selectedExportColumns.delete(colId);
      }
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function setAllColumns(select) {
      if (select) {
        selectedExportColumns = new Set(EXPORT_COLUMNS.map(c => c.id));
      } else {
        selectedExportColumns = new Set(['idx', 'name']);
      }
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function setStandardColumns() {
      selectedExportColumns = new Set(EXPORT_COLUMNS.filter(c => c.default).map(c => c.id));
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function setContactColumns() {
      selectedExportColumns = new Set(['idx', 'name', 'phase', 'track', 'phone', 'email', 'interview_slot']);
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function setEvalColumns() {
      selectedExportColumns = new Set(['idx', 'name', 'phase', 'track', 'admission', 'interview_slot', 'status', 'seat', 'score', 'eval_notes']);
      renderColumnCheckboxes();
      renderExportPreview();
    }

    function onExportFilterChange() {
      exportFilters.track = document.getElementById('expFilterTrack')?.value || 'all';
      exportFilters.phase = document.getElementById('expFilterPhase')?.value || 'all';
      exportFilters.admission = document.getElementById('expFilterAdmission')?.value || 'all';
      exportFilters.status = document.getElementById('expFilterStatus')?.value || 'all';
      exportFilters.interviewDate = document.getElementById('expFilterInterviewDate')?.value || 'all';
      exportFilters.minGpa = parseFloat(document.getElementById('expFilterMinGpa')?.value || '0');
      exportFilters.rank = document.getElementById('expFilterRank')?.value || 'all';
      exportFilters.uni = document.getElementById('expFilterUni')?.value || 'all';
      exportFilters.starred = document.getElementById('expFilterStarred')?.value || 'all';
      exportFilters.query = (document.getElementById('expSearchQuery')?.value || '').trim().toLowerCase();

      renderExportPreview();
    }

    function resetExportFilters() {
      exportFilters = {
        track: 'all',
        phase: 'all',
        admission: 'all',
        status: 'all',
        interviewDate: 'all',
        minGpa: 0,
        rank: 'all',
        uni: 'all',
        starred: 'all',
        query: ''
      };

      const setSelect = (id, val) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (Array.from(el.options).some(o => o.value === val)) {
          el.value = val;
          return;
        }
        const matchingOpt = Array.from(el.options).find(o => o.value.includes(val) || o.text.includes(val));
        if (matchingOpt) {
          el.value = matchingOpt.value;
          if (id === 'expFilterInterviewDate') exportFilters.interviewDate = matchingOpt.value;
        } else {
          el.value = val;
        }
      };
      setSelect('expFilterTrack', 'all');
      setSelect('expFilterPhase', 'all');
      setSelect('expFilterAdmission', 'all');
      setSelect('expFilterStatus', 'all');
      setSelect('expFilterInterviewDate', 'all');
      setSelect('expFilterMinGpa', '0');
      setSelect('expFilterRank', 'all');
      setSelect('expFilterUni', 'all');
      setSelect('expFilterStarred', 'all');
      const qInput = document.getElementById('expSearchQuery');
      if (qInput) qInput.value = '';

      renderExportPreview();
    }

    function applyExportPreset(presetType) {
      resetExportFilters();

      const setSelect = (id, val) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (Array.from(el.options).some(o => o.value === val)) {
          el.value = val;
          return;
        }
        const matchingOpt = Array.from(el.options).find(o => o.value.includes(val) || o.text.includes(val));
        if (matchingOpt) {
          el.value = matchingOpt.value;
          if (id === 'expFilterInterviewDate') exportFilters.interviewDate = matchingOpt.value;
        } else {
          el.value = val;
        }
      };

      if (presetType === 'phase1') {
        exportFilters.phase = 'phase1';
        document.getElementById('expFilterPhase').value = 'phase1';
        setStandardColumns();
        showToast('🟣 فیلتر سریع داوطلبان فاز ۱ اعمال گردید');
      } else if (presetType === 'phase2') {
        exportFilters.phase = 'phase2';
        document.getElementById('expFilterPhase').value = 'phase2';
        setStandardColumns();
        showToast('🔵 فیلتر سریع داوطلبان فاز ۲ اعمال گردید');
      } else if (presetType === 'phase3') {
        exportFilters.phase = 'phase3';
        document.getElementById('expFilterPhase').value = 'phase3';
        setStandardColumns();
        showToast('🟠 فیلتر سریع داوطلبان فاز ۳ اعمال گردید');
      } else if (presetType === 'phase12') {
        exportFilters.phase = 'phase12';
        document.getElementById('expFilterPhase').value = 'phase12';
        setStandardColumns();
        showToast('🎯 فیلتر داوطلبان فاز ۱ و فاز ۲ اعمال گردید');
      } else if (presetType === 'accepted') {
        exportFilters.status = 'accepted';
        document.getElementById('expFilterStatus').value = 'accepted';
        selectedExportColumns.add('seat');
        renderColumnCheckboxes();
        showToast('🌟 فیلتر پذیرفته‌شدگان قطعی ظرفیت آزمایشگاه اعمال شد');
      } else if (presetType === 'invited') {
        exportFilters.status = 'invited';
        document.getElementById('expFilterStatus').value = 'invited';
        setEvalColumns();
        showToast('📅 فیلتر کلیه متقاضیان دعوت‌شده به مصاحبه اعمال شد');
      } else if (presetType === 'interview_tuesday') {
        exportFilters.interviewDate = '۱۹ آبان';
        setSelect('expFilterInterviewDate', '۱۹ آبان');
        setEvalColumns();
        showToast('🗓️ جلسات مصاحبه سه‌شنبه ۱۹ آبان فعال شدند');
      } else if (presetType === 'interview_wednesday') {
        exportFilters.interviewDate = '۲۰ آبان';
        setSelect('expFilterInterviewDate', '۲۰ آبان');
        setEvalColumns();
        showToast('🗓️ جلسات مصاحبه چهارشنبه ۲۰ آبان فعال شدند');
      } else if (presetType === 'interview_saturday') {
        exportFilters.interviewDate = '۲۴ آبان';
        setSelect('expFilterInterviewDate', '۲۴ آبان');
        setEvalColumns();
        showToast('🗓️ جلسات مصاحبه شنبه ۲۴ آبان فعال شدند');
      } else if (presetType === 'talented') {
        exportFilters.admission = 'talented';
        document.getElementById('expFilterAdmission').value = 'talented';
        showToast('🏆 فیلتر متقاضیان استعداد درخشان اعمال گردید');
      } else if (presetType === 'contacts') {
        setContactColumns();
        showToast('📞 ستون‌های تماس و هماهنگی فعال شدند');
      } else if (presetType === 'all_data') {
        setAllColumns(true);
        showToast('📑 تمام ۲۲ ستون پرونده فعال شدند');
      }

      renderExportPreview();
    }

    function getFilteredExportCandidates() {
      let list = candidates.filter(c => {
        // Track
        if (exportFilters.track === 'AI' && c.track_en !== 'AI') return false;
        if (exportFilters.track === 'Software' && c.track_en !== 'Software') return false;

        // Phase
        if (exportFilters.phase === 'phase1' && c.interview_phase !== 'phase1') return false;
        if (exportFilters.phase === 'phase2' && c.interview_phase !== 'phase2') return false;
        if (exportFilters.phase === 'phase3' && c.interview_phase !== 'phase3') return false;
        if (exportFilters.phase === 'phase12' && c.interview_phase !== 'phase1' && c.interview_phase !== 'phase2') return false;
        if (exportFilters.phase === 'nophase' && c.interview_phase) return false;

        // Admission
        if (exportFilters.admission === 'rozaneh' && !(c.admission_type?.includes('روزانه') || c.quota?.includes('روزانه') || c.quota?.includes('استعداد') || c.quota?.includes('بورس'))) return false;
        if (exportFilters.admission === 'shabaneh' && !(c.admission_type?.includes('شبانه') || c.quota?.includes('شبانه'))) return false;
        if (exportFilters.admission === 'talented' && !(c.admission_type?.includes('استعداد') || c.quota?.includes('استعداد'))) return false;

        // Status
        if (exportFilters.status === 'accepted' && !isCandidateAssigned(c.id)) return false;
        if (exportFilters.status === 'invited' && c.status !== 'دعوت به مصاحبه') return false;
        if (exportFilters.status === 'rejected' && !(c.status === 'رد شده' || c.status === 'عدم پذیرش')) return false;
        if (exportFilters.status === 'pending' && (c.status === 'رد شده' || c.status === 'عدم پذیرش' || c.status === 'دعوت به مصاحبه' || isCandidateAssigned(c.id))) return false;

        // Interview Date Filter
        if (exportFilters.interviewDate === 'has_date') {
          if (!c.interview_slot || !c.interview_slot.trim()) return false;
        } else if (exportFilters.interviewDate === 'no_date') {
          if (c.interview_slot && c.interview_slot.trim()) return false;
        } else if (exportFilters.interviewDate && exportFilters.interviewDate !== 'all') {
          if (!c.interview_slot || !c.interview_slot.includes(exportFilters.interviewDate)) return false;
        }

        // Min GPA
        if (exportFilters.minGpa > 0 && (c.gpa_val || 0) < exportFilters.minGpa) return false;

        // Rank
        if (exportFilters.rank !== 'all') {
          const maxR = parseInt(exportFilters.rank);
          if ((c.rank_val || 999) > maxR) return false;
        }

        // University
        if (exportFilters.uni !== 'all') {
          if (!c.bsc_uni || !c.bsc_uni.includes(exportFilters.uni)) return false;
        }

        // Starred
        if (exportFilters.starred === 'starred' && !starredIds.has(c.id)) return false;

        // Free search query
        if (exportFilters.query) {
          const str = (c.name + ' ' + c.bsc_uni + ' ' + c.high_school + ' ' + c.skills + ' ' + c.konkur_arshad + ' ' + (c.interests||'')).toLowerCase();
          if (!str.includes(exportFilters.query)) return false;
        }

        return true;
      });

      // Sort chronologically if filtering by interview date or when interview slot filter is active
      if (exportFilters.interviewDate && exportFilters.interviewDate !== 'all' && exportFilters.interviewDate !== 'no_date') {
        list.sort((a, b) => (a.interview_slot || '').localeCompare(b.interview_slot || ''));
      }

      return list;
    }

    function getExportFilterDescription() {
      const parts = [];
      if (exportFilters.track === 'AI') parts.push('هوش مصنوعی');
      else if (exportFilters.track === 'Software') parts.push('نرم‌افزار');
      else parts.push('همه گرایش‌ها');

      if (exportFilters.phase === 'phase1') parts.push('فاز ۱');
      else if (exportFilters.phase === 'phase2') parts.push('فاز ۲');
      else if (exportFilters.phase === 'phase3') parts.push('فاز ۳');
      else if (exportFilters.phase === 'phase12') parts.push('فاز ۱ و ۲');
      else if (exportFilters.phase === 'nophase') parts.push('بدون فاز');

      if (exportFilters.admission !== 'all') parts.push(exportFilters.admission);
      if (exportFilters.status !== 'all') parts.push(exportFilters.status);
      if (exportFilters.interviewDate === 'has_date') parts.push('دارای تاریخ مصاحبه');
      else if (exportFilters.interviewDate === 'no_date') parts.push('بدون تاریخ مصاحبه');
      else if (exportFilters.interviewDate && exportFilters.interviewDate !== 'all') parts.push(`تاریخ مصاحبه: ${exportFilters.interviewDate}`);

      if (exportFilters.minGpa > 0) parts.push(`معدل بالای ${exportFilters.minGpa}`);
      if (exportFilters.uni !== 'all') parts.push(exportFilters.uni);
      if (exportFilters.query) parts.push(`جستجو: «${exportFilters.query}»`);

      return parts.join(' · ');
    }

    function renderExportPreview() {
      const thead = document.getElementById('exportPreviewHead');
      const tbody = document.getElementById('exportPreviewBody');
      if (!thead || !tbody) return;

      const filtered = getFilteredExportCandidates();
      const activeCols = EXPORT_COLUMNS.filter(c => selectedExportColumns.has(c.id));

      // Update Summary Info
      const statsSummary = document.getElementById('exportStatsSummary');
      if (statsSummary) {
        statsSummary.textContent = `تعداد رکوردهای منطبق: ${filtered.length} داوطلب (از ${candidates.length} نفر) · ${activeCols.length} ستون فعال`;
      }
      const descSummary = document.getElementById('exportFilterDescSummary');
      if (descSummary) {
        descSummary.textContent = `فیلتر فعال: ${getExportFilterDescription()}`;
      }

      // Build Thead
      thead.innerHTML = `
        <tr>
          ${activeCols.map(col => `<th style="text-align: center; white-space: nowrap;">${col.label}</th>`).join('')}
        </tr>
      `;

      // Build Tbody
      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${activeCols.length || 1}" style="text-align: center; padding: 24px; color: var(--color-ink-muted);">هیچ داوطلبی مطابق با شروط فیلتر انتخاب‌شده یافت نشد.</td></tr>`;
        return;
      }

      tbody.innerHTML = '';
      filtered.forEach((cand, idx) => {
        const tr = document.createElement('tr');
        const isRejected = cand.status === 'رد شده' || cand.status === 'عدم پذیرش';
        if (isRejected) tr.className = 'row-rejected';

        tr.innerHTML = activeCols.map(col => {
          const val = col.getValue(cand, idx);
          const isCenter = ['idx', 'phase', 'track', 'bsc_gpa', 'rank_arshad', 'interview_slot', 'status', 'score', 'phone'].includes(col.id);
          
          let cellContent = val;
          if (col.id === 'phase') {
            cellContent = cand.interview_phase 
              ? `<span class="badge-pill phase-${cand.interview_phase}">${getPhaseLabelShort(cand.interview_phase)}</span>`
              : '<span style="color:var(--color-ink-muted); font-size:10.5px;">بدون فاز</span>';
          } else if (col.id === 'track') {
            cellContent = `<span class="badge-pill ${cand.track_en === 'AI' ? 'ai' : 'sw'}">${cand.track}</span>`;
          } else if (col.id === 'name') {
            cellContent = `<b class="${isRejected ? 'name-strikethrough' : ''}">${cand.name}</b>`;
          } else if (col.id === 'bsc_gpa') {
            cellContent = `<span style="color:var(--color-stamp); font-weight:800;">${cand.bsc_gpa}</span>`;
          }

          return `<td style="text-align: ${isCenter ? 'center' : 'right'}; font-size: 11px; white-space: ${col.id === 'exp' || col.id === 'interests' || col.id === 'eval_notes' ? 'normal' : 'nowrap'};">${cellContent}</td>`;
        }).join('');

        tbody.appendChild(tr);
      });
    }

    function renderExportStudio() {
      initExportStudio();
    }

    function executeExport(format) {
      if (format === 'excel') exportToExcel();
      else if (format === 'csv') exportToCsv();
      else if (format === 'pdf') exportToPdfReport();
      else if (format === 'copy') copyExportTableToClipboard();
    }

    function exportToExcel() {
      const filtered = getFilteredExportCandidates();
      if (filtered.length === 0) {
        showToast('⚠️ داوطلبی مطابق با فیلترهای انتخابی یافت نشد.');
        return;
      }
      const activeCols = EXPORT_COLUMNS.filter(c => selectedExportColumns.has(c.id));
      const headers = activeCols.map(c => c.label);
      const rows = filtered.map((cand, idx) => activeCols.map(c => c.getValue(cand, idx)));
      const filterDesc = getExportFilterDescription();

      showToast('⏳ در حال آماده‌سازی فایل اکسل پیشرفته...');

      // Try Server API first
      fetch('/api/export/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          headers: headers,
          rows: rows,
          title: 'فهرست متقاضیان منتخب آزمایشگاه داده‌کاوی (DML) - ورودی‌های ارشد ۱۴۰۵',
          filter_desc: filterDesc
        })
      })
      .then(res => {
        if (!res.ok) throw new Error('Server error');
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dml_candidates_export_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('✔️ فایل اکسل پیشرفته با موفقیت دانلود گردید');
      })
      .catch(() => {
        // Fallback to client-side SheetJS if server unavailable or in standalone
        if (typeof XLSX !== 'undefined') {
          const aoa = [headers, ...rows];
          const ws = XLSX.utils.aoa_to_sheet(aoa);
          ws['!dir'] = 'rtl';
          const wb = XLSX.utils.book_new();
          XLSX.utils.book_append_sheet(wb, ws, 'متقاضیان');
          XLSX.writeFile(wb, `dml_candidates_export_${new Date().toISOString().slice(0,10)}.xlsx`);
          showToast('✔️ فایل اکسل با موفقیت تولید و دانلود شد');
        } else {
          exportToCsv();
        }
      });
    }

    function exportToCsv() {
      const filtered = getFilteredExportCandidates();
      if (filtered.length === 0) {
        showToast('⚠️ داوطلبی مطابق با فیلترهای انتخابی یافت نشد.');
        return;
      }
      const activeCols = EXPORT_COLUMNS.filter(c => selectedExportColumns.has(c.id));
      const headers = activeCols.map(c => `"${c.label.replace(/"/g, '""')}"`);
      
      const csvLines = [headers.join(',')];
      filtered.forEach((cand, idx) => {
        const line = activeCols.map(c => {
          const val = String(c.getValue(cand, idx) ?? '').replace(/"/g, '""');
          return `"${val}"`;
        });
        csvLines.push(line.join(','));
      });

      const csvContent = '\uFEFF' + csvLines.join('\r\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dml_candidates_export_${new Date().toISOString().slice(0,10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast('✔️ فایل CSV با موفقیت دانلود شد');
    }

    function exportToPdfReport() {
      const filtered = getFilteredExportCandidates();
      if (filtered.length === 0) {
        showToast('⚠️ داوطلبی مطابق با فیلترهای انتخابی یافت نشد.');
        return;
      }
      const activeCols = EXPORT_COLUMNS.filter(c => selectedExportColumns.has(c.id));
      const headers = activeCols.map(c => c.label);
      const rows = filtered.map((cand, idx) => activeCols.map(c => c.getValue(cand, idx)));
      const filterDesc = getExportFilterDescription();

      showToast('⏳ در حال آماده‌سازی و ساخت فایل PDF رسمی...');

      // Try Server API first for direct PDF file download
      fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          headers: headers,
          rows: rows,
          title: 'فهرست متقاضیان منتخب آزمایشگاه داده‌کاوی (DML) - ورودی‌های ارشد ۱۴۰۵',
          filter_desc: filterDesc
        })
      })
      .then(res => {
        if (!res.ok) throw new Error('Server error');
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dml_candidates_export_${new Date().toISOString().slice(0,10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('✔️ فایل PDF رسمی با موفقیت دانلود شد');
      })
      .catch(() => {
        // Fallback for standalone / offline mode
        fallbackPrintPdf(headers, rows, filterDesc);
      });
    }

    function fallbackPrintPdf(headers, rows, filterDesc) {
      const printWin = window.open('', '_blank', 'width=1200,height=850');
      if (!printWin) {
        showToast('⚠️ پاپ‌آپ چاپ مسدود شد. لطفاً اجازه باز شدن پنجره را بدهید.');
        return;
      }
      const dateStr = new Date().toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' });
      const isLandscape = headers.length > 5;
      const pageSize = isLandscape ? 'A4 landscape' : 'A4 portrait';

      let fontSize = '9.5px';
      let padding = '5px 6px';
      if (headers.length <= 5) { fontSize = '10.5px'; padding = '6px 8px'; }
      else if (headers.length <= 8) { fontSize = '9.5px'; padding = '5px 6px'; }
      else if (headers.length <= 12) { fontSize = '8px'; padding = '4px 5px'; }
      else if (headers.length <= 16) { fontSize = '7.2px'; padding = '3px 4px'; }
      else { fontSize = '6.5px'; padding = '2.5px 3px'; }

      const thHtml = headers.map(h => `<th style="background:#1B365D; color:#FFFFFF; padding:${padding}; border:1px solid #0F172A; font-weight:800; text-align:center;">${h}</th>`).join('');
      const trHtml = rows.map((r, rIdx) => {
        const bg = rIdx % 2 === 0 ? '#FFFFFF' : '#F8FAFC';
        const cells = r.map((val, cIdx) => {
          const hText = headers[cIdx] || '';
          const isCenter = ['ردیف', 'معدل', 'رتبه', 'گرایش', 'فاز', 'ساعت', 'تلفن', 'نمره', 'وضعیت'].some(k => hText.includes(k));
          let valStr = String(val ?? '');
          if (hText.includes('فاز')) {
            if (valStr.includes('فاز ۱')) valStr = `<span style="background:#F3E8FF; color:#6D28D9; border:1px solid #8B5CF6; border-radius:3px; padding:1px 4px; font-weight:800;">${valStr}</span>`;
            else if (valStr.includes('فاز ۲')) valStr = `<span style="background:#E0F2FE; color:#0369A1; border:1px solid #38BDF8; border-radius:3px; padding:1px 4px; font-weight:800;">${valStr}</span>`;
            else if (valStr.includes('فاز ۳')) valStr = `<span style="background:#FEF3C7; color:#B45309; border:1px solid #F59E0B; border-radius:3px; padding:1px 4px; font-weight:800;">${valStr}</span>`;
          } else if (hText.includes('گرایش')) {
            if (valStr.includes('هوش')) valStr = `<span style="background:#E6F5F6; color:#0E7C86; border:1px solid #0E7C86; border-radius:3px; padding:1px 4px; font-weight:800;">${valStr}</span>`;
            else if (valStr.includes('نرم')) valStr = `<span style="background:#FDEEEB; color:#C0392B; border:1px solid #C0392B; border-radius:3px; padding:1px 4px; font-weight:800;">${valStr}</span>`;
          } else if (hText.includes('نام')) {
            valStr = `<b>${valStr}</b>`;
          }
          return `<td style="padding:${padding}; border:1px solid #CBD5E1; text-align:${isCenter ? 'center' : 'right'}; font-size:${fontSize};">${valStr}</td>`;
        }).join('');
        return `<tr style="background:${bg};">${cells}</tr>`;
      }).join('');

      printWin.document.write(`<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>خروجی رسمی متقاضیان منتخب DML</title>
  <style>
    @page { size: ${pageSize}; margin: 8mm 10mm; }
    body { font-family: 'Vazirmatn', Tahoma, sans-serif; direction: rtl; margin: 0; padding: 12px; color: #1A1915; font-size: ${fontSize}; line-height: 1.4; }
    table { width: 100%; border-collapse: collapse; font-size: ${fontSize}; table-layout: auto; word-break: break-word; }
    tr { page-break-inside: avoid; }
    thead { display: table-header-group; }
  </style>
</head>
<body>
  <div style="border-bottom: 2px solid #1B365D; padding-bottom: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
    <div>
      <h1 style="margin: 0 0 2px 0; font-size: 14px; font-weight: 900; color: #1B365D;">دانشگاه علم و صنعت ایران</h1>
      <h2 style="margin: 0; font-size: 10.5px; font-weight: 700; color: #475569;">دانشکده مهندسی کامپیوتر · آزمایشگاه داده‌کاوی (DML)</h2>
    </div>
    <div style="text-align: center;">
      <h3 style="margin: 0 0 2px 0; font-size: 13.5px; font-weight: 900; color: #1B365D;">فهرست متقاضیان منتخب آزمایشگاه داده‌کاوی</h3>
      <div style="font-size: 9.5px; color: #64748B; font-weight: 700;">پذیرش کارشناسی ارشد ورودی‌های ۱۴۰۵</div>
    </div>
    <div style="text-align: left; font-size: 9px; color: #475569;">
      <div><b>تاریخ:</b> ${dateStr}</div>
      <div><b>استاد راهنما:</b> دکتر بهروز مینایی بیدگلی</div>
      <div><b>تعداد رکوردها:</b> ${rows.length} نفر</div>
    </div>
  </div>
  <div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px 8px; margin-bottom: 8px; font-size: 8.5px; display: flex; justify-content: space-between;">
    <div><b>فیلترها:</b> ${filterDesc}</div>
    <div><b>منتخب:</b> ${rows.length} داوطلب</div>
  </div>
  <table>
    <thead><tr>${thHtml}</tr></thead>
    <tbody>${trHtml}</tbody>
  </table>
  <div style="margin-top: 15px; padding-top: 8px; border-top: 1px dashed #94A3B8; display: flex; justify-content: space-between; align-items: flex-end; font-size: 8.5px; page-break-inside: avoid;">
    <div style="color: #64748B;">گزارش رسمی استخراج‌شده از کارتابل جامع پذیرش DML</div>
    <div style="text-align: center; min-width: 160px;">
      <div style="font-weight: 800; color: #1B365D;">استاد راهنما و مدیر آزمایشگاه</div>
      <div style="font-weight: 700; color: #334155; margin-top: 2px;">دکتر بهروز مینایی بیدگلی</div>
      <div style="margin-top: 30px; border-top: 1px dotted #64748B; width: 110px; margin-inline: auto;">امضاء و تاریخ</div>
    </div>
  </div>
</body>
</html>`);
      printWin.document.close();
      printWin.focus();
      setTimeout(() => {
        printWin.print();
      }, 500);
    }

    function copyExportTableToClipboard() {
      const filtered = getFilteredExportCandidates();
      if (filtered.length === 0) {
        showToast('⚠️ داوطلبی برای کپی یافت نشد.');
        return;
      }
      const activeCols = EXPORT_COLUMNS.filter(c => selectedExportColumns.has(c.id));
      const headers = activeCols.map(c => c.label);
      
      const tsvLines = [headers.join('\t')];
      filtered.forEach((cand, idx) => {
        const line = activeCols.map(c => String(c.getValue(cand, idx) ?? '').replace(/[\t\r\n]+/g, ' '));
        tsvLines.push(line.join('\t'));
      });

      const tsvContent = tsvLines.join('\n');
      navigator.clipboard.writeText(tsvContent)
        .then(() => {
          showToast('📋 جدول با موفقیت در کلیپ‌بورد کپی شد (آماده Paste در اکسل/Word)');
        })
        .catch(() => {
          showToast('❌ خطا در دسترسی به کلیپ‌بورد');
        });
    }


    window.addEventListener('DOMContentLoaded', () => {
      initData();
      renderSeatsBoard();
      renderRoster();
      renderTimetable();
      renderFilesExplorer();
      initExportStudio();
      syncWithServer();
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDossierModal();
        closeSeatPickerModal();
        closeEmailModal();
        closeShamsiPickerModal();
      }
    });
  </script>
</body>
</html>
"""

def build_seats_html(is_standalone=False):
    candidates_json_str = get_candidates_json(is_standalone)
    config_json_str = json.dumps(config, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__RAW_CANDIDATES_JSON__", candidates_json_str)
    html = html.replace("__CONFIG_JSON__", config_json_str)
    html = html.replace("__LAB_NAME__", config.get("lab_name", "آزمایشگاه"))
    html = html.replace("__LAB_SHORT__", config.get("lab_short", "LAB"))
    html = html.replace("__INSTITUTION__", config.get("institution", "دانشگاه"))
    html = html.replace("__DEPARTMENT__", config.get("department", "دانشکده"))
    html = html.replace("__SUPERVISOR__", config.get("supervisor_name", "استاد راهنما"))
    html = html.replace("__ACADEMIC_YEAR__", config.get("academic_year", "۱۴۰۵ - ۱۴۰۶"))
    html = html.replace("__LOCATION_DEFAULT__", config.get("interview_location_default", "اتاق آزمایشگاه"))
    html = html.replace("__MAP_URL__", config.get("interview_map_url", ""))
    return html

if __name__ == '__main__':
    templates_index = os.path.join(CORE_DIR, "templates", "index.html")
    with open(templates_index, "w", encoding="utf-8") as f:
        f.write(build_seats_html(is_standalone=False))
    print(f"{templates_index} updated successfully.")

    # Generate offline dashboard at project root
    out_path = os.path.join(PROJECT_ROOT, "offline_dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_seats_html(is_standalone=True))
    print(f"{out_path} updated successfully.")
