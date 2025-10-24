# AI-Based Resume Analyzer (Lightweight, Rule-Based)

Lightweight resume parsing and matching web app that extracts skills, education and roles from resumes (CSV / PDF / DOCX), scores resumes against job descriptions using rule-based matching (keyword overlap + weighted scoring), and returns ranked results with downloadable CSVs. This repo intentionally avoids heavy semantic/embedding models — it uses simple, fast heuristics so it can run locally or on small servers.

## Quick summary
- One-line: Fast, explainable resume parser and JD matcher using keyword lists and rule-based scoring.
- Semantic matching: NOT used. Matching is based on keyword/role/education overlap (see scripts/parse_resumes.py and scripts/match_resumes.py).
- Target users: developers building recruitment tooling, career coaches, or anyone who needs a lightweight, local resume analysis pipeline.

## Features
- Web UI (Flask) to upload resume CSV / PDF / DOCX and provide/select job descriptions.
- Resume parsing into structured fields: resume_id, skills, education, roles (scripts/parse_resumes.py).
- Scoring/matching resumes to JDs using weighted overlap of skills, roles and education (scripts/match_resumes.py).
- Small utilities:
  - build_vocab.py — build a simple vocabulary from a dataset.
  - create_eval_csv.py — sample resumes and pair with example JDs for evaluation.
- Persisted custom JDs in `jd_store.json`.
- Temporary output CSV download for scored results.

## How it works (high level)
- app.py handles uploads, JD management (saved + custom + CSV JDs), text extraction (pdfplumber / PyPDF2 / python-docx fallback), and orchestrates parsing + matching.
- parse_resumes.py uses internal keyword lists (`skills_list`, `education_list`, `roles_list`) and substring matching to extract structured fields.
- match_resumes.py computes overlap-based scores:
  - skill_score (50% weight), role_score (30%), edu_score (20%).
  - Score per JD is normalized and returned with matched items.
- Output: JSON results for the UI and a CSV saved to `output/` for download.

## Repo layout (important files)
- app.py — Flask web app and frontend integration (templates/index.html).
- templates/index.html — Bootstrap UI and client-side JS fetch to /analyze.
- scripts/
  - parse_resumes.py — parsing logic (keyword/substr-based).
  - match_resumes.py — scoring/matching logic (overlap-based).
  - build_vocab.py — simple vocab builder from dataset.
  - create_eval_csv.py — create `output/evaluation_data.csv` for manual evaluation.
- Dataset/Resume.csv — default dataset (not included in repo).
- jd_store.json — saved custom JDs (created at runtime).
- output/ — generated CSVs: parsed_resumes.csv, resume_scores.csv, evaluation_data.csv.

## Quickstart (local)
1. Clone the repo:
   git clone <repo-url>
2. Create and activate a Python venv:
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .venv\Scripts\activate     # Windows
3. Install dependencies:
```bash
pip install -r requirements.txt
```
(See a suggested requirements.txt below.)
4. Run the web app:
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

5. Alternative CLI scripts:
- Parse resumes and save output:
```bash
python scripts/parse_resumes.py -i Dataset/Resume.csv
```
- Match resumes to default JDs:
```bash
python scripts/match_resumes.py -i Dataset/Resume.csv
```
- Build vocab from dataset:
```bash
python scripts/build_vocab.py -i Dataset/Resume.csv
```
- Generate sampled evaluation CSV:
```bash
python scripts/create_eval_csv.py -i Dataset/Resume.csv -n 50
```

## API endpoints (implemented in app.py)
- GET / — main UI
- GET /jds — list default and saved JDs (JSON)
- POST /add_jd — add a custom JD (form or JSON); saves to jd_store.json
- POST /analyze — upload resumes and/or JDs and get matching results (JSON + downloadable CSV)
- GET /download/<filename> — download generated CSV from system temp folder

## Example scoring behavior
- A JD with skills ["Python", "SQL", "AI"]:
  - If a parsed resume lists "Python, AI" (2/3 skill match) and a role match is present, score = 0.5*(2/3) + role_score*0.3 + edu_score*0.2.
- Results include matched skill/role/education strings so the decision is explainable.

## Why rule-based (and limitations)
- Pros:
  - Fast, low-resource, explainable, easy to run locally.
  - No need for GPU/large model downloads.
- Cons:
  - Limited to keyword overlaps; lacks deep semantic understanding (e.g., synonyms, paraphrases, implicit skills).
  - Requires keeping keyword lists up to date and may need fuzzy matching to improve recall.

## How to extend (suggestions)
- Improve parsing:
  - Use spaCy (NER, matcher) or a fine-tuned model for better extraction.
  - Add fuzzy matching (rapidfuzz) to catch small spelling variations.
  - Add date parsing (dateutil) to extract experience durations.
- Replace or augment matching:
  - Add TF-IDF + cosine similarity (scikit-learn) for document-level similarity.
  - Add semantic embeddings via sentence-transformers if you accept heavier models (for better role-fit).
- Add OCR improvements for scanned PDFs via cloud OCR (Google Vision, AWS Textract) or Tesseract for more robust extraction.
- Add authentication, retention policies, and job queues (Celery, RQ) for scaling.

## Privacy & data handling
- Uploaded files are saved briefly to temp files and removed when possible.
- jd_store.json persists custom JDs; add deletion endpoints if you need stricter policies.
- If you process sensitive resumes, run the app in an isolated environment and consider adding:
  - At-rest encryption for stored files
  - Automatic deletion after X days
  - Local-only processing mode (no external APIs)

## Suggested requirements.txt
```text
Flask>=2.0
pandas>=1.3
pdfplumber>=0.6   # optional, improves PDF extraction
PyPDF2>=2.0       # fallback for PDF extraction
python-docx>=0.8  # optional, for DOCX extraction
openpyxl>=3.0     # if you add Excel support
```
Add other libs (spaCy, scikit-learn, sentence-transformers, rapidfuzz) only if you adopt those improvements.

## Example LICENSE
Consider MIT or Apache-2.0 for permissive open-source licensing.

## Contribution
- Expand keyword lists in scripts/parse_resumes.py (skills_list, education_list, roles_list).
- Add tests for parsing and matching.
- Provide optional config (YAML/JSON) to load skill/role lists instead of editing code.

---

ou want to optionally enable embeddings.

Tell me which of the above you'd like me to create next and I will produce it (a requirements.txt, CONTRIBUTING.md, or code changes).
