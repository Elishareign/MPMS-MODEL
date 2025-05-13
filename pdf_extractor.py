import fitz
import os

def extract_text_from_pdfs(folder_path):
    extracted_texts = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            extracted_texts[filename] = text
    return extracted_texts
