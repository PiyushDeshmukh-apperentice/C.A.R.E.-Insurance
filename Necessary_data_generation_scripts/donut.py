from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

# -----------------------------
# Load model
# -----------------------------
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
model = VisionEncoderDecoderModel.from_pretrained(
    "naver-clova-ix/donut-base-finetuned-docvqa"
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# -----------------------------
# Ask question
# -----------------------------
def ask_doc_question(image_path, question):
    image = Image.open(image_path).convert("RGB")

    prompt = f"<s_docvqa><question>{question}</question><answer>"

    inputs = processor(image, prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_length=256
    )

    answer = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    return answer

# -----------------------------
# Example
# -----------------------------
if __name__ == "__main__":
    print(ask_doc_question("/mnt/StorageHDD/PICT/synthetic.png", "What is the name of the hospital?"))
    # print(ask_doc_question("scan.jpg", "What imaging test was performed?"))
    # print(ask_doc_question("scan.jpg", "What procedure was done?"))
