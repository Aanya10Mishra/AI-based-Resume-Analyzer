# create_eval_csv.py
# Description: Create an evaluation CSV by sampling resumes and pairing with example JDs.
# Behavior: Takes a dataset path as input (optional). If not provided it uses "Dataset/Resume.csv".
# Outputs: automatically saves to "output/evaluation_data.csv" (no need to pass an output path).
#
# Place this file in your project root (same folder that contains Dataset/, output/, scripts/).
# Run: python create_eval_csv.py
# Or:  python create_eval_csv.py -i "C:/full/path/to/Resume.csv"

import os
import argparse
import random
import pandas as pd

# -------------------------
# EDIT ONLY THIS DEFAULT if you want a different default dataset path
DEFAULT_INPUT = r"C:\Users\Manvi\Documents\AI based resume analyzer\Dataset\Resume.csv"
OUTPUT_EVAL = "output/evaluation_data.csv"
SAMPLE_SIZE_DEFAULT = 30
# -------------------------

def main():
    ap = argparse.ArgumentParser(description="Create evaluation CSV from dataset (sampled).")
    ap.add_argument("--input", "-i", required=False, default=DEFAULT_INPUT,
                    help=f"Path to resume CSV (default: {DEFAULT_INPUT})")
    ap.add_argument("--sample-size", "-n", required=False, type=int, default=SAMPLE_SIZE_DEFAULT,
                    help=f"Number of resumes to sample (default: {SAMPLE_SIZE_DEFAULT})")
    args = ap.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} resumes from {input_path}")

    job_descriptions = [
        {"jd_id": "JD1", "title": "Software Engineer", "skills": ["Python", "Machine Learning", "AI", "SQL"]},
        {"jd_id": "JD2", "title": "Data Analyst", "skills": ["Excel", "Power BI", "Statistics", "Python"]},
        {"jd_id": "JD3", "title": "Graphic Designer", "skills": ["Photoshop", "Illustrator", "Creativity"]},
        {"jd_id": "JD4", "title": "HR Manager", "skills": ["Recruitment", "Communication", "Payroll", "Leadership"]}
    ]

    sample_size = min(args.sample_size, len(df))
    eval_data = []
    for _, row in df.sample(sample_size).iterrows():
        jd = random.choice(job_descriptions)
        resume_text = str(row.get("Resume_str", row.get("resume_text", "")))[:800]
        matched_skills = [s for s in jd["skills"] if s.lower() in resume_text.lower()]
        eval_data.append({
            "resume_id": row.get("ID", ""),
            "jd_id": jd["jd_id"],
            "jd_title": jd["title"],
            "jd_skills": ", ".join(jd["skills"]),
            "relevance_score": random.randint(0, 3),
            "matched_skills": ", ".join(matched_skills),
            "resume_text_snippet": resume_text[:300]
        })

    os.makedirs(os.path.dirname(OUTPUT_EVAL) or "output", exist_ok=True)
    pd.DataFrame(eval_data).to_csv(OUTPUT_EVAL, index=False)
    print(f"Saved evaluation CSV to: {OUTPUT_EVAL} (sampled {sample_size} resumes)")


if __name__ == "__main__":
    main()
