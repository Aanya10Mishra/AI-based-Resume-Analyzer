# build_vocab.py
# Description: Build simple vocab (skills, roles, education) from dataset text column.
# Behavior: Takes a dataset path as input (optional). If not provided it uses "Dataset/Resume.csv".
# Outputs: automatically saves to "output/kaggle_vocab.pkl" (no need to pass an output path).
#
# Place this file in your project root (same folder that contains Dataset/, output/, scripts/).
# Run: python build_vocab.py
# Or:  python build_vocab.py -i "C:/full/path/to/Resume.csv"

import os
import argparse
import pandas as pd
import pickle

# -------------------------
# EDIT ONLY THIS DEFAULT if you want a different default dataset path
DEFAULT_INPUT = r"C:\Users\Manvi\Documents\AI based resume analyzer\Dataset\Resume.csv"
OUTPUT_VOCAB = "kaggle_vocab.pkl"
# -------------------------

def build_vocab_from_df(df, text_col="Resume_str"):
    skills_vocab = set()
    roles_vocab = set()
    edu_vocab = set()

    edu_keywords = ["B.Tech", "M.Tech", "B.Sc", "MBA", "B.Des", "Diploma", "BBA", "PhD", "BE", "MSc", "BCA", "MCA"]
    role_keywords = ["Software Engineer", "Data Analyst", "HR Manager", "Graphic Designer", "Teacher", "Consultant"]

    for text in df[text_col].fillna("").astype(str):
        words = set([w.strip().title() for w in text.split()])
        skills_vocab.update(words)
        for r in role_keywords:
            if r.lower() in text.lower():
                roles_vocab.add(r)
        for e in edu_keywords:
            if e.lower() in text.lower():
                edu_vocab.add(e)

    return {"skills": sorted(skills_vocab), "roles": sorted(roles_vocab), "edu": sorted(edu_vocab)}


def main():
    ap = argparse.ArgumentParser(description="Build vocab from resume CSV.")
    ap.add_argument("--input", "-i", required=False, default=DEFAULT_INPUT,
                    help=f"Path to resume CSV (default: {DEFAULT_INPUT})")
    args = ap.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    if "resume_text" in df.columns and "Resume_str" not in df.columns:
        df = df.rename(columns={"resume_text": "Resume_str"})
    vocab = build_vocab_from_df(df, text_col="Resume_str")

    os.makedirs(os.path.dirname(OUTPUT_VOCAB) or ".", exist_ok=True)
    with open(OUTPUT_VOCAB, "wb") as f:
        pickle.dump(vocab, f)
    print(f"Saved vocab to: {OUTPUT_VOCAB} (skills: {len(vocab['skills'])}, roles: {len(vocab['roles'])}, edu: {len(vocab['edu'])})")


if __name__ == "__main__":
    main()
