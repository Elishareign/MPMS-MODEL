1. **Clone this repo:**

    ```bash
    git clone https://github.com/Elishareign/MPMS-MODEL.git


2. **Create a virtual environment and activate it**
  
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate

3. **Install dependencies**

    pip install -r requirements.txt

4. **Download spaCy model (if not already)**

    python -m spacy download en_core_web_md

5. **Run the Streamlit app**

    streamlit run app.py
