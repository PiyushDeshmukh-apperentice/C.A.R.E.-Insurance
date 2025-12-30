import pandas as pd
import os
import shutil

# -------------------------
# Hard-coded paths (EDIT THESE)
# -------------------------

CLINICAL_NOTES_DIR = r"/mnt/StorageHDD/PICT/codiesp/final_dataset_v4_to_publish/dev/text_files_en"     # Folder containing all .txt notes
OUTPUT_DIR = r"/mnt/StorageHDD/PICT/processed_data/digestive_disease_data/clinical_notes"      # Where to store filtered notes

CSV_MAIN = r"/mnt/StorageHDD/PICT/codiesp/final_dataset_v4_to_publish/dev/devD.tsv"       # Contains: filename, icd
CSV_PROCEDURE = r"/mnt/StorageHDD/PICT/codiesp/final_dataset_v4_to_publish/dev/devP.tsv"      # Contains: filename, icd

OUTPUT_CSV = r"/mnt/StorageHDD/PICT/processed_data/digestive_disease_data/combined.csv"         # NEW CSV output path


# -------------------------
# Load CSVs
# -------------------------

df_main = pd.read_csv(CSV_MAIN)
df_proc = pd.read_csv(CSV_PROCEDURE)

# Normalize column names
for df in [df_main, df_proc]:
    df.columns = [c.lower() for c in df.columns]


# -------------------------
# Filter MAIN ICDs starting with "C"
# -------------------------

df_main_c = df_main[df_main['icd'].astype(str).str.startswith('k')]

print(f"Main ICDs starting with C: {len(df_main_c)}")


# -------------------------
# Merge PROCEDURE ICDs
# -------------------------

df_proc_unique = df_proc.drop_duplicates("filename")

df_merged = df_main_c.merge(
    df_proc_unique,
    on="filename",
    how="left",
    suffixes=("_main", "_procedure")
)

df_merged.rename(columns={"icd_main": "main_icd", "icd_procedure": "procedure_icd"}, inplace=True)

# Reorder columns
df_merged = df_merged[["filename", "main_icd", "procedure_icd"]]


# -------------------------
# Save merged CSV
# -------------------------

df_merged.to_csv(OUTPUT_CSV, index=False)
print(f"Saved C-related mapping CSV: {OUTPUT_CSV}")


# -------------------------
# Copy all matched .txt files
# -------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

missing = []
copied = 0

for fname in df_merged["filename"].unique():

    # Auto-correct missing .txt extension
    if not fname.lower().endswith(".txt"):
        fname_txt = fname + ".txt"
    else:
        fname_txt = fname

    txt_path = os.path.join(CLINICAL_NOTES_DIR, fname_txt)

    if os.path.exists(txt_path):
        shutil.copy(txt_path, os.path.join(OUTPUT_DIR, fname_txt))
        copied += 1
    else:
        missing.append(fname_txt)

print(f"Copied: {copied} notes")
print(f"Missing: {len(missing)}")

if missing:
    print("Missing files:")
    for m in missing:
        print("  -", m)

