#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic Admission Studio - Candidate Importer
Utility to import applicants from Excel/CSV or automatically discover folders in resumes/
"""

import os
import sys
import json
import argparse

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOLS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESUMES_DIR = os.path.join(PROJECT_ROOT, "resumes")
DATA_FILE = os.path.join(DATA_DIR, "candidates_data.json")

def scan_resumes_folder():
    """
    Scans resumes/ directory structured as:
    resumes/<Track>/<CandidateName>/[files...]
    and generates candidate records.
    """
    if not os.path.exists(RESUMES_DIR):
        print(f"❌ Error: {RESUMES_DIR} directory does not exist.")
        return []

    candidates = []
    cid = 1

    tracks = [d for d in os.listdir(RESUMES_DIR) if os.path.isdir(os.path.join(RESUMES_DIR, d)) and not d.startswith('.')]
    tracks.sort()

    for track in tracks:
        track_dir = os.path.join(RESUMES_DIR, track)
        candidate_folders = [f for f in os.listdir(track_dir) if os.path.isdir(os.path.join(track_dir, f)) and not f.startswith('.')]
        candidate_folders.sort()

        for folder_name in candidate_folders:
            c_dir = os.path.join(track_dir, folder_name)
            files = []
            primary_pdf = None
            email_body = ""

            for fname in os.listdir(c_dir):
                if fname.startswith('.'):
                    continue
                fpath = os.path.join(c_dir, fname)
                is_pdf = fname.lower().endswith(".pdf")
                is_txt = fname.lower().endswith(".txt")
                size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
                rel_url = f"/files/{track}/{folder_name}/{fname}"

                files.append({
                    "name": fname,
                    "path": f"{track}/{folder_name}/{fname}",
                    "rel_url": rel_url,
                    "size": size,
                    "size_str": size_str,
                    "is_pdf": is_pdf,
                    "is_txt": is_txt
                })

                if is_pdf and (primary_pdf is None or "cv" in fname.lower() or "resume" in fname.lower()):
                    primary_pdf = rel_url
                
                if fname.lower() in ["main.txt", "email.txt", "cover.txt"]:
                    try:
                        with open(fpath, "r", encoding="utf-8") as tf:
                            email_body = tf.read()
                    except Exception:
                        pass

            if not primary_pdf and files:
                primary_pdf = files[0]["rel_url"]

            # Generate initials
            parts = folder_name.strip().split()
            initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')) if parts else '--'

            cand = {
                "id": cid,
                "name": folder_name,
                "initials": initials,
                "track": track,
                "track_en": track,
                "quota": "سراسری / استعداد درخشان",
                "admission_type": "بررسی اولیه",
                "konkur_arshad": "-",
                "bsc_major": "مهندسی کامپیوتر",
                "bsc_gpa": "۱۸.۰۰",
                "bsc_uni": "-",
                "konkur_bsc": "-",
                "high_school": "-",
                "phone": "-",
                "notes": f"متقاضی دوره تحصیلات تکمیلی گرایش {track}",
                "interests": "پژوهش و توسعه سیستم‌های نرم‌افزاری و هوش مصنوعی",
                "email": f"{folder_name.lower().replace(' ', '.')}@example.com",
                "social": "-",
                "skills": "Python, Git, Linux",
                "exp": "-",
                "priority": "اولویت اول",
                "color": "#0E7C86" if "ai" in track.lower() or "هوش" in track else "#C0392B",
                "folder": folder_name,
                "folder_rel": f"{track}/{folder_name}",
                "files": files,
                "primary_pdf": primary_pdf or "",
                "email_body": email_body,
                "interview_slot": "",
                "interview_type": "حضوری",
                "status": "بررسی اولیه",
                "score": None,
                "eval_notes": "",
                "seat_cx": 100.0 + (cid % 4) * 80.0,
                "seat_cy": 200.0 + (cid // 4) * 80.0,
                "seat_deg": 180.0,
                "rank_val": cid * 10,
                "gpa_val": 18.0,
                "cluster": track,
                "matrix_x": 550.0,
                "matrix_y": 80.0,
                "interview_phase": None
            }
            candidates.append(cand)
            cid += 1

    return candidates

def import_from_csv(csv_path):
    import csv
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file {csv_path} not found.")
        return []

    candidates = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            name = row.get("name") or row.get("نام") or f"متقاضی {idx}"
            track = row.get("track") or row.get("گرایش") or "عمومی"
            gpa = row.get("gpa") or row.get("معدل") or "17.0"
            rank = row.get("rank") or row.get("رتبه") or "100"
            phone = row.get("phone") or row.get("تلفن") or "-"
            email = row.get("email") or row.get("ایمیل") or "-"

            try:
                gpa_val = float(gpa.replace('/', '.'))
            except Exception:
                gpa_val = 17.0

            try:
                rank_val = int(rank)
            except Exception:
                rank_val = 100

            cand = {
                "id": idx,
                "name": name,
                "initials": name[:2],
                "track": track,
                "track_en": track,
                "quota": row.get("quota") or row.get("سهمیه") or "سراسری",
                "admission_type": row.get("admission_type") or "کنکور سراسری",
                "konkur_arshad": f"رتبه {rank_val}",
                "bsc_major": row.get("bsc_major") or "مهندسی کامپیوتر",
                "bsc_gpa": str(gpa_val),
                "bsc_uni": row.get("uni") or row.get("دانشگاه") or "-",
                "phone": phone,
                "email": email,
                "notes": row.get("notes") or "",
                "interests": row.get("interests") or "",
                "skills": row.get("skills") or "Python",
                "exp": row.get("exp") or "-",
                "priority": "اولویت اول",
                "color": "#0E7C86",
                "folder": name,
                "folder_rel": f"{track}/{name}",
                "files": [],
                "primary_pdf": "",
                "email_body": "",
                "interview_slot": "",
                "interview_type": "حضوری",
                "status": "بررسی اولیه",
                "score": None,
                "eval_notes": "",
                "seat_cx": 100.0,
                "seat_cy": 200.0,
                "seat_deg": 180.0,
                "rank_val": rank_val,
                "gpa_val": gpa_val,
                "cluster": track,
                "matrix_x": 550.0,
                "matrix_y": 80.0,
                "interview_phase": None
            }
            candidates.append(cand)
    return candidates

def main():
    parser = argparse.ArgumentParser(description="Academic Admission Studio - Data Importer")
    parser.add_argument("--scan-resumes", action="store_true", help="Auto-scan resumes/ directory structure")
    parser.add_argument("--csv", type=str, help="Path to input CSV file")
    parser.add_argument("--out", type=str, default=DATA_FILE, help="Path to output candidates_data.json")

    args = parser.parse_args()

    candidates = []
    if args.scan_resumes:
        print("📂 Scanning resumes/ directory...")
        candidates = scan_resumes_folder()
    elif args.csv:
        print(f"📊 Reading CSV file from {args.csv}...")
        candidates = import_from_csv(args.csv)
    else:
        print("💡 Hint: Run with --scan-resumes to scan the resumes/ folder, or --csv <file.csv> to import from CSV.")
        return

    if candidates:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully imported {len(candidates)} candidates to {args.out}")
        print("🔄 Recompiling dashboard UI...")
        try:
            import subprocess
            gen_script = os.path.join(PROJECT_ROOT, "core", "generate_seats_ui.py")
            subprocess.check_call([sys.executable, gen_script])
            print("✨ Dashboard updated successfully!")
        except Exception as e:
            print("⚠️ Note: please run 'python core/generate_seats_ui.py' to update HTML views.")
    else:
        print("⚠️ No candidates found to import.")

if __name__ == "__main__":
    main()
