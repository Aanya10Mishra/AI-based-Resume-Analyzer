# parse_resumes.py
# Description: Parse a resume CSV into structured fields (resume_id, skills, education, roles).
# Behavior: Takes a dataset path as input (optional). If not provided it uses "Dataset/Resume.csv".
# Outputs: automatically saves to "output/parsed_resumes.csv" (no need to pass an output path).
#
# Place this file in your project root (same folder that contains Dataset/, output/, scripts/).
# Run: python parse_resumes.py
# Or:  python parse_resumes.py -i "C:/full/path/to/Resume.csv"

import os
import argparse
import pandas as pd

# -------------------------
# EDIT ONLY THIS DEFAULT if you want a different default dataset path
DEFAULT_INPUT = r"C:\Users\Manvi\Documents\AI based resume analyzer\Dataset\Resume.csv"  # relative path recommended; can be absolute (use r"..." if contains backslashes)
OUTPUT_PARSED = "output/parsed_resumes.csv"  # fixed output path (script writes here automatically)
# -------------------------

# Simple keyword lists (expandable)
skills_list = [
    "Python", "Java", "C++", "SQL", "Machine Learning", "AI", "Excel",
    "Power BI", "Statistics", "Photoshop", "Illustrator", "Communication",
    "Leadership", "Recruitment", "Payroll", "Deep Learning", "NLP"
]
education_list = [
    "B.Tech", "BE", "M.Tech", "ME", "MBA", "B.Sc", "M.Sc", "PhD",
    "Diploma", "High School", "Intermediate", "BCA", "MCA"
]
roles_list = [
    "Software Engineer", "Data Analyst", "Graphic Designer", "HR Manager",
    "Teacher", "Consultant", "Accountant", "Engineer", "Finance Manager",
    "Sales Executive"
]


def extract_skills(text):
    text_lower = str(text).lower()
    matched = [skill for skill in skills_list if skill.lower() in text_lower]
    return ", ".join(matched)


def extract_education(text):
    text_lower = str(text).lower()
    matched = [edu for edu in education_list if edu.lower() in text_lower]
    return ", ".join(matched)


def extract_roles(text):
    text_lower = str(text).lower()
    matched = [role for role in roles_list if role.lower() in text_lower]
    return ", ".join(matched)


def parse_resumes_df(df, text_col="resume_text", id_col="ID"):
    """
    Parse resume DataFrame and return DataFrame with columns:
    resume_id, skills, education, roles
    """
    parsed_data = []
    has_id = id_col in df.columns
    for idx, row in df.iterrows():
        resume_text = str(row.get(text_col, ""))
        resume_id = row.get(id_col, idx) if has_id else idx
        parsed_data.append({
            "resume_id": resume_id,
            "skills": extract_skills(resume_text),
            "education": extract_education(resume_text),
            "roles": extract_roles(resume_text)
        })
    return pd.DataFrame(parsed_data)


def main():
    ap = argparse.ArgumentParser(description="Parse resumes CSV into structured fields.")
    ap.add_argument("--input", "-i", required=False, default=DEFAULT_INPUT,
                    help=f"Path to resume CSV (default: {DEFAULT_INPUT})")
    args = ap.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    # support older column name
    if "Resume_str" in df.columns and "resume_text" not in df.columns:
        df = df.rename(columns={"Resume_str": "resume_text"})
    parsed_df = parse_resumes_df(df, text_col="resume_text", id_col="ID")

    os.makedirs(os.path.dirname(OUTPUT_PARSED) or ".", exist_ok=True)
    parsed_df.to_csv(OUTPUT_PARSED, index=False)
    print(f"Saved parsed resumes to: {OUTPUT_PARSED}")


if __name__ == "__main__":
    main()