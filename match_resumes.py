# match_resumes.py
# Description: Parse the dataset (using parse_resumes.py) and score resumes against default JDs.
# Behavior: Takes a dataset path as input (optional). If not provided it uses "Dataset/Resume.csv".
# Outputs: automatically saves to "output/resume_scores.csv" (no need to pass an output path).
#
# Place this file in your project root (same folder that contains Dataset/, output/, scripts/).
# Run: python match_resumes.py
# Or:  python match_resumes.py -i "C:/full/path/to/Resume.csv"

import os
import argparse
import pandas as pd

# -------------------------
# EDIT ONLY THIS DEFAULT if you want a different default dataset path
DEFAULT_INPUT = r"C:\Users\Manvi\Documents\AI based resume analyzer\Dataset\Resume.csv"   # dataset CSV (relative recommended)
OUTPUT_SCORES = "output/resume_scores.csv"
# -------------------------

# Default job descriptions (edit here to add/modify JDs)
DEFAULT_JDS = [
    {"jd_id": "JD1", "title": "Software Engineer", "skills": ["Python", "Machine Learning", "AI", "SQL"], "roles": ["Software Engineer"]},
    {"jd_id": "JD2", "title": "Data Analyst", "skills": ["Excel", "Power BI", "Statistics", "Python"], "roles": ["Data Analyst"]},
    {"jd_id": "JD3", "title": "Graphic Designer", "skills": ["Photoshop", "Illustrator", "Creativity"], "roles": ["Graphic Designer"]},
    {"jd_id": "JD4", "title": "HR Manager", "skills": ["Recruitment", "Communication", "Payroll", "Leadership"], "roles": ["HR Manager"]}
]

# Try to import parse_resumes module in same folder for reuse; otherwise parse inline
try:
    import parse_resumes  # expects parse_resumes.py in same directory
    have_parser = True
except Exception:
    have_parser = False


def compute_similarity(resume_skills, resume_roles, resume_education, jd):
    resume_skills_set = set([s.strip().lower() for s in str(resume_skills).split(",") if s.strip()])
    resume_roles_set = set([r.strip().lower() for r in str(resume_roles).split(",") if r.strip()])
    resume_edu_set = set([e.strip().lower() for e in str(resume_education).split(",") if e.strip()])

    jd_skills_set = set([s.strip().lower() for s in jd.get("skills", [])])
    jd_roles_set = set([r.strip().lower() for r in jd.get("roles", [])])
    jd_edu_set = set([e.strip().lower() for e in jd.get("education", [])])

    skill_matches = resume_skills_set & jd_skills_set
    skill_score = len(skill_matches) / len(jd_skills_set) if jd_skills_set else 0

    role_matches = resume_roles_set & jd_roles_set
    role_score = len(role_matches) / len(jd_roles_set) if jd_roles_set else 0

    edu_matches = resume_edu_set & jd_edu_set
    edu_score = len(edu_matches) / len(jd_edu_set) if jd_edu_set else 0

    total_score = 0.5 * skill_score + 0.3 * role_score + 0.2 * edu_score
    return round(total_score, 2), skill_matches, role_matches, edu_matches


def match_all(parsed_df, job_descriptions):
    scored = []
    for _, row in parsed_df.iterrows():
        for jd in job_descriptions:
            score, skill_matches, role_matches, edu_matches = compute_similarity(
                row.get("skills", ""), row.get("roles", ""), row.get("education", ""), jd
            )
            scored.append({
                "resume_id": row.get("resume_id"),
                "jd_id": jd.get("jd_id"),
                "jd_title": jd.get("title"),
                "score": score,
                "skills_matched": ", ".join(sorted(skill_matches, key=str.lower)) if skill_matches else "",
                "roles_matched": ", ".join(sorted(role_matches, key=str.lower)) if role_matches else "",
                "education_matched": ", ".join(sorted(edu_matches, key=str.lower)) if edu_matches else ""
            })
    return pd.DataFrame(scored)


def main():
    ap = argparse.ArgumentParser(description="Parse dataset and score resumes against default JDs.")
    ap.add_argument("--input", "-i", required=False, default=DEFAULT_INPUT,
                    help=f"Path to resume CSV (default: {DEFAULT_INPUT})")
    args = ap.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    # Use parse_resumes module if available
    if have_parser:
        df = pd.read_csv(input_path)
        # normalize column name if needed
        if "Resume_str" in df.columns and "resume_text" not in df.columns:
            df = df.rename(columns={"Resume_str": "resume_text"})
        parsed_df = parse_resumes.parse_resumes_df(df, text_col="resume_text", id_col="ID")
    else:
        # Inline simple parser fallback (same logic as parse_resumes)
        df = pd.read_csv(input_path)
        if "Resume_str" in df.columns and "resume_text" not in df.columns:
            df = df.rename(columns={"Resume_str": "resume_text"})
        # simple parsing inline
        def extract_skills(text):
            text_lower = str(text).lower()
            # small set of skills for fallback
            skills = ["python", "java", "c++", "sql", "machine learning", "ai", "excel"]
            return ", ".join([s.title() for s in skills if s in text_lower])
        parsed_rows = []
        for idx, row in df.iterrows():
            resume_text = str(row.get("resume_text", ""))
            parsed_rows.append({
                "resume_id": row.get("ID", idx),
                "skills": extract_skills(resume_text),
                "education": "",
                "roles": ""
            })
        parsed_df = pd.DataFrame(parsed_rows)

    scored_df = match_all(parsed_df, DEFAULT_JDS)
    os.makedirs(os.path.dirname(OUTPUT_SCORES) or ".", exist_ok=True)
    scored_df.to_csv(OUTPUT_SCORES, index=False)
    print(f"Saved resume scores to: {OUTPUT_SCORES}")


if __name__ == "__main__":
    main()