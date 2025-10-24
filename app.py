# app.py
# Adds dynamic JD support: paste a JD, upload JD CSV, or use saved JDs (jd_store.json).
# Place this file in your project root and run: python .\app.py

import os
import sys
import json
import tempfile
import pandas as pd
from flask import Flask, render_template, request, jsonify, url_for, send_file

# Make scripts/ importable
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "scripts")
if os.path.isdir(SCRIPT_DIR) and SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import existing modules (must be in scripts/)
import parse_resumes as parser
import match_resumes as matcher

# Optional: text-extraction imports for pdf/docx (if your app already has them)
try:
    import pdfplumber
except Exception:
    pdfplumber = None
try:
    import docx
except Exception:
    docx = None
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

app = Flask(__name__, template_folder="templates")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_KAGGLE_PATH = os.path.join(PROJECT_ROOT, "Dataset", "Resume.csv")
OUTPUT_TMP_DIR = tempfile.gettempdir()
JD_STORE_PATH = os.path.join(PROJECT_ROOT, "jd_store.json")  # persist custom JDs here

# Default example JDs (fallback)
DEFAULT_JOB_DESCRIPTIONS = [
    {"jd_id": "JD1", "title": "Software Engineer",
     "skills": ["Python", "Machine Learning", "AI", "SQL"], "roles": ["Software Engineer"]},
    {"jd_id": "JD2", "title": "Data Analyst",
     "skills": ["Excel", "Power BI", "Statistics", "Python"], "roles": ["Data Analyst"]},
    {"jd_id": "JD3", "title": "Graphic Designer",
     "skills": ["Photoshop", "Illustrator", "Creativity"], "roles": ["Graphic Designer"]},
    {"jd_id": "JD4", "title": "HR Manager",
     "skills": ["Recruitment", "Communication", "Payroll", "Leadership"], "roles": ["HR Manager"]}
]


def load_saved_jds():
    if not os.path.exists(JD_STORE_PATH):
        return []
    try:
        with open(JD_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_jd_to_store(jd):
    jds = load_saved_jds()
    jds.append(jd)
    with open(JD_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(jds, f, indent=2, ensure_ascii=False)
    return jd


def extract_text_from_pdf(path):
    text_parts = []
    if pdfplumber:
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text() or ""
                    text_parts.append(txt)
            return "\n".join(text_parts).strip()
        except Exception:
            pass
    if PdfReader:
        try:
            reader = PdfReader(path)
            for p in reader.pages:
                try:
                    txt = p.extract_text() or ""
                    text_parts.append(txt)
                except Exception:
                    continue
            return "\n".join(text_parts).strip()
        except Exception:
            pass
    return ""


def extract_text_from_docx(path):
    if not docx:
        return ""
    try:
        document = docx.Document(path)
        paras = [p.text for p in document.paragraphs if p.text]
        return "\n".join(paras).strip()
    except Exception:
        return ""


def file_to_dataframe(uploaded_file_path, original_filename):
    ext = original_filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        df = pd.read_csv(uploaded_file_path)
        if "Resume_str" in df.columns and "resume_text" not in df.columns:
            df = df.rename(columns={"Resume_str": "resume_text"})
        return df
    elif ext == "pdf":
        text = extract_text_from_pdf(uploaded_file_path)
        return pd.DataFrame([{"resume_text": text, "ID": original_filename}])
    elif ext == "docx":
        text = extract_text_from_docx(uploaded_file_path)
        return pd.DataFrame([{"resume_text": text, "ID": original_filename}])
    else:
        return pd.DataFrame(columns=["resume_text"])


def extract_skills_from_text(jd_text):
    """
    Lightweight skill/role extraction from JD text:
    - Uses the parser's skills_list (if available) for exact matches
    - Falls back to selecting frequent capitalized tokens as candidate skills
    """
    jd_text = str(jd_text or "")
    skills_found = set()
    # try parse_resumes' internal list if present
    try:
        skill_candidates = getattr(parser, "skills_list", [])
        for s in skill_candidates:
            if s.lower() in jd_text.lower():
                skills_found.add(s)
    except Exception:
        pass

    # quick heuristic: pick capitalized words/phrases (2-word phrases) as extra candidates
    words = [w.strip() for w in jd_text.replace("\n", " ").split() if w.strip()]
    caps = []
    for i, w in enumerate(words):
        if w[:1].isupper() and len(w) > 1:
            caps.append(w)
            # try two-word phrase
            if i + 1 < len(words) and words[i + 1][:1].isupper():
                caps.append(f"{w} {words[i+1]}")
    for c in caps[:30]:
        # add if not too long and not common stop words
        if len(c) < 40:
            skills_found.add(c)
    return sorted(skills_found)


@app.route("/")
def index():
    saved = load_saved_jds()
    return render_template("index.html", jds=DEFAULT_JOB_DESCRIPTIONS + saved)


@app.route("/jds", methods=["GET"])
def list_jds():
    saved = load_saved_jds()
    return jsonify({"default_jds": DEFAULT_JOB_DESCRIPTIONS, "saved_jds": saved})


@app.route("/add_jd", methods=["POST"])
def add_jd():
    """
    Add a custom JD via POST JSON or form fields.
    Accepts:
      - title (string)
      - jd_text (string)
      - optional skills (comma-separated) OR roles (comma-separated)
    Returns the saved JD with jd_id.
    """
    data = request.form.to_dict() or request.get_json() or {}
    title = data.get("title") or data.get("jd_title") or "Custom JD"
    jd_text = data.get("jd_text", "")
    skills_field = data.get("skills", "")
    roles_field = data.get("roles", "")

    if not jd_text and not skills_field:
        return jsonify({"error": "Provide jd_text or skills"}), 400

    skills = [s.strip() for s in skills_field.split(",") if s.strip()] if skills_field else extract_skills_from_text(jd_text)
    roles = [r.strip() for r in roles_field.split(",") if r.strip()]

    # generate jd_id
    saved = load_saved_jds()
    next_id = len(saved) + 1
    jd_id = f"CUST{next_id:03d}"
    jd = {"jd_id": jd_id, "title": title, "skills": skills, "roles": roles, "source_text": jd_text[:200]}
    save_jd_to_store(jd)
    return jsonify({"saved": jd})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze form accepts:
    - use_default_dataset checkbox
    - resume_csv file (csv/pdf/docx)
    - jd_select (JD id or 'ALL')
    - OR jd_text field containing a custom JD to analyze against
    - OR upload a JD CSV file named jd_csv with columns jd_id,title,skills,roles
    """
    use_default = request.form.get("use_default_dataset") == "on"
    jd_select = request.form.get("jd_select", "ALL")
    jd_text = request.form.get("jd_text", "").strip()

    # Get dataset DataFrame (same as before)
    if use_default:
        if not os.path.exists(DEFAULT_KAGGLE_PATH):
            return jsonify({"error": f"Default dataset not found at {DEFAULT_KAGGLE_PATH}"}), 400
        df = pd.read_csv(DEFAULT_KAGGLE_PATH)
        if "Resume_str" in df.columns and "resume_text" not in df.columns:
            df = df.rename(columns={"Resume_str": "resume_text"})
    else:
        if "resume_csv" not in request.files:
            return jsonify({"error": "No resume file uploaded and default dataset not selected."}), 400
        uploaded = request.files["resume_csv"]
        if uploaded.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        # save to temp file and convert
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded.filename.rsplit(".", 1)[-1])
        uploaded.save(tmp.name)
        try:
            df = file_to_dataframe(tmp.name, uploaded.filename)
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

    if df.empty or ("resume_text" not in df.columns and "Resume_str" not in df.columns):
        return jsonify({"error": "Uploaded file did not contain resume text (need Resume_str or resume_text)"}), 400
    if "Resume_str" in df.columns and "resume_text" not in df.columns:
        df = df.rename(columns={"Resume_str": "resume_text"})

    # Determine JD(s) to use
    jds_to_score = []
    # 1) If jd_text provided in form -> use it as single custom JD
    if jd_text:
        skills = extract_skills_from_text(jd_text)
        custom_jd = {"jd_id": "CUSTOM", "title": "Custom JD", "skills": skills, "roles": []}
        jds_to_score = [custom_jd]
    # 2) If a JD CSV was uploaded in jd_csv field -> parse and use those JDs
    elif "jd_csv" in request.files and request.files["jd_csv"].filename:
        jdfile = request.files["jd_csv"]
        tmp_j = tempfile.NamedTemporaryFile(delete=False, suffix="." + jdfile.filename.rsplit(".", 1)[-1])
        jdfile.save(tmp_j.name)
        try:
            jd_df = pd.read_csv(tmp_j.name)
            for _, r in jd_df.fillna("").iterrows():
                jd_id = str(r.get("jd_id") or r.get("id") or r.get("title")[:6])
                title = str(r.get("title") or "")
                skills = [s.strip() for s in str(r.get("skills", "")).split(",") if s.strip()]
                roles = [s.strip() for s in str(r.get("roles", "")).split(",") if s.strip()]
                jds_to_score.append({"jd_id": jd_id, "title": title, "skills": skills, "roles": roles})
        finally:
            try:
                os.unlink(tmp_j.name)
            except Exception:
                pass
    # 3) If jd_select is a saved or default JD id -> load it
    elif jd_select and jd_select != "ALL" and jd_select != "":
        # check saved JDs
        saved_jds = load_saved_jds()
        found = next((x for x in saved_jds if x["jd_id"] == jd_select), None)
        if found:
            jds_to_score = [found]
        else:
            # check default JDs
            found2 = next((x for x in DEFAULT_JOB_DESCRIPTIONS if x["jd_id"] == jd_select), None)
            if found2:
                jds_to_score = [found2]

    # 4) default fallback -> all default JDs
    if not jds_to_score:
        jds_to_score = DEFAULT_JOB_DESCRIPTIONS

    # Parse resumes using parser.parse_resumes_df
    parsed_df = parser.parse_resumes_df(df, text_col="resume_text", id_col="ID")

    # Score
    scored_df = matcher.match_all(parsed_df, jds_to_score)

    # Save temp CSV for download
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", prefix="resume_scores_")
    scored_df.to_csv(tmp_out.name, index=False)
    tmp_out.close()
    download_url = url_for("download_results", filename=os.path.basename(tmp_out.name))

    # Prepare results summary
    results = []
    for jd in jds_to_score:
        jd_scores = scored_df[scored_df["jd_id"] == jd["jd_id"]].sort_values(by="score", ascending=False).head(30)
        results.append({"jd_id": jd["jd_id"], "jd_title": jd.get("title", ""), "top_matches": jd_scores.to_dict(orient="records")})

    # optional: return the extracted snippet when single resume uploaded (helps user confirm extraction)
    extracted_snippet = None
    if len(df) == 1:
        extracted_snippet = str(df.iloc[0].get("resume_text", ""))[:400]

    return jsonify({"results": results, "download_url": download_url, "extracted_snippet": extracted_snippet})


@app.route("/download/<path:filename>", methods=["GET"])
def download_results(filename):
    fullpath = os.path.join(OUTPUT_TMP_DIR, filename)
    if not os.path.exists(fullpath):
        return jsonify({"error": "File not found"}), 404
    return send_file(fullpath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    # create store if missing
    if not os.path.exists(JD_STORE_PATH):
        with open(JD_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    app.run(debug=True, port=5000)