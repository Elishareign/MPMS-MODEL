# Profile Parser

first draft of Profile Parsing & Text Analysis module of MPMS built with Streamlit that extracts structured information from PDF resumes

## features

- extract text from PDF resumes
- identify contact information, skills, education, experience, and certifications
- visualize skills with word clouds
- export parsed data as JSON
- view structured data in tables

## Setup

1. clone the repository
- (optional) also you can setup a virtual environment as well
   ``` python -m venv venv ```
   then activate it with
   ``` venv/scripts/activate ```
2. run the setup script:
   ```
   python setup.py
   ```
3. run the streamlit app:
   ```
   streamlit run app.py
   ```

## notes
- work in progress
-  not yet optimized for large and in different format resumes 
- mainly used yesha's and my cv for testing

## requirements

- python 3.7+
- see requirements.txt for package dependencies