import fitz  
import os

# Path to the folder containing the PDFs
folder_path = "Data"

# To loop the folder content 
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):  
        file_path = os.path.join(folder_path, filename)
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()


        print(f"----- {filename} -----")
        print(text[:500])
        print("\n")
