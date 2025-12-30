from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from pathlib import Path
import json

# --------------------------------------------------
# HARDCODED PATHS
# --------------------------------------------------
INPUT_DOCUMENT = Path(
    "/mnt/StorageHDD/PICT/digestive_disease/template3_documents_AGED/medium/S1130-63432016000400011-1/6_bill.pdf"
)

OUTPUT_JSON = Path(
    "/mnt/StorageHDD/PICT/full_text.json"
)

OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# LINE-WISE OCR EXTRACTION
# --------------------------------------------------
def extract_lines_doctr(doc_path: Path, output_json: Path):

    # Load document
    if doc_path.suffix.lower() == ".pdf":
        doc = DocumentFile.from_pdf(doc_path)
    else:
        doc = DocumentFile.from_images(doc_path)

    # OCR model
    model = ocr_predictor(
        det_arch="db_resnet50",
        reco_arch="crnn_vgg16_bn",
        pretrained=True
    )

    # Run OCR
    result = model(doc)

    extracted = {
        "document_path": str(doc_path),
        "pages": [],
        "full_text": ""
    }

    for page_idx, page in enumerate(result.pages):

        page_lines = []

        for block in page.blocks:
            for line in block.lines:
                line_text = " ".join(w.value for w in line.words)

                if line_text.strip():
                    page_lines.append({
                        "text": line_text,
                        "bbox": line.geometry   # keep if needed
                    })

        page_data = {
            "page_index": page_idx,
            "dimensions": page.dimensions,
            "lines": page_lines,
            "page_text": "\n".join(l["text"] for l in page_lines)
        }

        extracted["pages"].append(page_data)
        extracted["full_text"] += page_data["page_text"] + "\n"

    # Save output
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    print(f"Line-wise OCR extraction completed → {output_json}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    extract_lines_doctr(INPUT_DOCUMENT, OUTPUT_JSON)
