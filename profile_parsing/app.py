import streamlit as st
import spacy
from typing import List, Dict, Tuple, Optional
from io import BytesIO
import re
import pandas as pd
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import fitz
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# import from the modularized text_preprocessing package
from text_preprocessing import (
    preprocess_text,
    extract_skills,
    extract_education,
    extract_experience,
    extract_certifications,
    extract_named_entities,
    extract_contact_info,
    extract_summary
)

# load spaCy model
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Profile Parser", layout="wide")
st.title("📄 Profile Parsing & Text Analysis Module")

def extract_text_from_pdf(pdf_file) -> str:
    """
    extracts text from a PDF using multiple methods for maximum coverage
    regardless of PDF length or complexity || DRAFT 1 ||
    """
    try:
        # store the original file content to reset pointer between extraction attempts
        pdf_content = pdf_file.read()
        pdf_file.seek(0)
        
        extracted_texts = []
        
        # method 1: pdrminer.six with optimized params for text extraction
        try:
            # try different LAParams configs for better extraction
            laparams_configs = [
                # standard config
                LAParams(line_margin=0.5, word_margin=0.1, char_margin=2.0, all_texts=True),
                # more aggressive for tightly packed text
                LAParams(line_margin=0.3, word_margin=0.05, char_margin=1.5, all_texts=True),
                # more lenient for widely spaced text
                LAParams(line_margin=0.8, word_margin=0.2, char_margin=3.0, all_texts=True)
            ]
            
            for laparams in laparams_configs:
                try:
                    # creates a new bytesio for each attemtp
                    pdf_bytes = BytesIO(pdf_content)
                    text = extract_text(pdf_bytes, laparams=laparams).strip()
                    if text:
                        extracted_texts.append(text)
                except Exception as e:
                    st.warning(f"pdfminer extraction attempt failed: {str(e)}")
        except ImportError:
            st.warning("pdfminer.six not available. Install with: pip install pdfminer.six")
        
        # method 2: PyMuPDF (fitz) for better hadnling of formatted PDFs
        try: 
            pdf_bytes = BytesIO(pdf_content)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # extract text page by page with diff methods
            pymupdf_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # method 2.1: Standard text extraction
                page_text = page.get_text()
                
                # Method 2.2: try with diff text extarction flags if standard is too short
                if len(page_text.strip()) < 100:
                    page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
                
                #method 2.3" try with blocks for structured text  
                if len(page_text.strip()) < 100:
                    blocks = page.get_text("blocks")
                    page_text = "\n".join([b[4] for b in blocks])
                
                pymupdf_text += page_text + "\n"
            
            doc.close()
            if pymupdf_text.strip():
                extracted_texts.append(pymupdf_text.strip())
        except ImportError:
            st.warning("PyMuPDF not available. Install with: pip install pymupdf")
        except Exception as e:
            st.warning(f"PyMuPDF extraction failed: {str(e)}")
        
        # choose the better extraction resukt
        if extracted_texts:
            # sort by length and take the longest result
            best_text = max(extracted_texts, key=len)
            
            # clean up the etxt while preserving importanvt structure
            best_text = re.sub(r' {2,}', ' ', best_text)
            best_text = re.sub(r' *\n *', '\n', best_text)
            best_text = re.sub(r'\n{3,}', '\n\n', best_text)
            
            # reset file pointer for potentaial future use
            pdf_file.seek(0)
            
            return best_text
        else:
            st.error("All extraction methods failed. The PDF might be encrypted, scanned without OCR, or corrupted.")
            return ""
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return ""

def identify_resume_sections(text: str) -> Dict[str, str]:
    """
    identifies common resume sections based on headers
    """
    sections = {}
    
    # common section headers in resumes
    section_patterns = {
        'personal_info': r'(?:PERSONAL INFORMATION|PERSONAL DETAILS|CONTACT|PROFILE)',
        'summary': r'(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE|ABOUT ME)',
        'skills': r'(?:SKILLS|TECHNICAL SKILLS|EXPERTISE|COMPETENCIES)',
        'experience': r'(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|WORK HISTORY)',
        'education': r'(?:EDUCATION|ACADEMIC|QUALIFICATIONS)',
        'certifications': r'(?:CERTIFICATIONS|CERTIFICATES|COURSES)',
        'projects': r'(?:PROJECTS|PROJECT EXPERIENCE)',
        'languages': r'(?:LANGUAGES|LANGUAGE PROFICIENCY)',
        'interests': r'(?:INTERESTS|HOBBIES)'
    }
    
    # find the sections in raw text
    lines = text.split('\n')
    current_section = 'unknown'
    sections[current_section] = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # check if this line is a section header
        is_header = False
        for section, pattern in section_patterns.items():
            if re.match(f"^{pattern}\\s*:?$", line.upper()):
                current_section = section
                sections[current_section] = ""
                is_header = True
                break
                
        if not is_header:
            sections[current_section] += line + "\n"
    
    return sections

def create_downloadable_json(data: Dict) -> None:
    """
    creates a downloadable JSON file from the parsed resume data
    """
    import json
    
    # convert data into json
    json_str = json.dumps(data, indent=2)
    
    # create a dl button
    st.download_button(
        label="Download Parsed Data as JSON",
        data=json_str,
        file_name="resume_parsed_data.json",
        mime="application/json"
    )

def format_experience_for_display(experiences: List[Dict]) -> List[Dict]:
    """
    formats experience data for better display in the UI
    """
    formatted_exp = []
    
    for exp in experiences:
        title = exp.get('title', '')
        project = exp.get('project', '')
        
        if title == project:
            project = ""
        
        if project and title and project != title:
            display_title = f"{title} - {project}"
        elif project:
            display_title = project
        else:
            display_title = title
            
        if not display_title or display_title.isspace():
            display_title = "Project/Position"
            
        formatted_exp.append({
            'display_title': display_title,
            'title': title,
            'project': project,
            'technologies': exp.get('technologies', []),
            'description': exp.get('description', '')
        })
        
    return formatted_exp

# UI 
uploaded_file = st.file_uploader("Upload your CV/Resume (PDF only)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting and analyzing text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

        if extracted_text:
            #creates tabs for diff views
            raw_tab, analyzed_tab, structured_tab, export_tab = st.tabs(["Raw Text", "Analysis Results", "Structured Data", "Export"])
            
            with raw_tab:
                st.subheader("Extracted Text")
                st.text_area("Raw Resume Text", value=extracted_text, height=300)
                
                # identify sections
                sections = identify_resume_sections(extracted_text)
                if len(sections) > 1:  # ff found sections beyond 'unknown'
                    st.subheader("Detected Sections")
                    for section, content in sections.items():
                        if section != 'unknown' and content.strip():
                            with st.expander(f"{section.replace('_', ' ').title()}"):
                                st.text(content)
            
            # extract all data
            contact_info = extract_contact_info(extracted_text)
            summary = extract_summary(extracted_text)
            skills = extract_skills(extracted_text)
            experiences = extract_experience(extracted_text)
            education = extract_education(extracted_text)
            certifications = extract_certifications(extracted_text)
            entities = extract_named_entities(extracted_text)
            
            # format experiences
            formatted_experiences = format_experience_for_display(experiences)
            
            with analyzed_tab:
                st.subheader("Text Analysis Results")
                
                # CONTACT INFO
                st.markdown("### Contact Information")
                if contact_info:
                    for key, value in contact_info.items():
                        st.write(f"**{key.title()}:** {value}")
                else:
                    st.write("No contact information found")
                
                # SUMMARY
                if summary:
                    st.markdown("### Professional Summary")
                    st.write(summary)
                
                # SKILLS in table
                st.markdown("### Skills")
                if skills:
                    # create columns for skills display
                    num_columns = 3
                    columns = st.columns(num_columns)
                    skills_per_column = len(skills) // num_columns + (1 if len(skills) % num_columns > 0 else 0)
                    
                    for i, skill in enumerate(skills):
                        col_index = i // skills_per_column
                        with columns[col_index]:
                            st.write(f"• {skill}")
                else:
                    st.write("No skills found")

                # EXPERIENCE with better formatting
                st.markdown("### Experience & Projects")
                if formatted_experiences:
                    for exp in formatted_experiences:
                        with st.expander(f"{exp['display_title']}"):
                            if exp['technologies']:
                                st.write(f"**Technologies:** {', '.join(exp['technologies'])}")
                            st.markdown(f"**Description:** {exp['description']}")
                else:
                    st.write("No experience or projects found")

                # EDUCATION with better formatting
                st.markdown("### Education")
                if education:
                    for edu in education:
                        st.write(f"**{edu['level']}**")
                        if edu['school']:
                            st.write(f"• School: {edu['school']}")
                        if edu['year']:
                            st.write(f"• Year: {edu['year']}")
                        if edu.get('additional') and edu['additional']:
                            st.write(f"• Additional: {edu['additional']}")
                else:
                    st.write("No education details found")
                
                # CERTIFICATIONS
                st.markdown("### Certifications & Awards")
                if certifications and certifications[0] != "No certifications or awards found.":
                    for cert in certifications:
                        st.write(f"• {cert}")
                else:
                    st.write("No certifications or awards found")

            with structured_tab:
                st.subheader("Named Entity Recognition")
                
                # NER
                entity_types = {
                    'PERSON': '👤 People',
                    'ORG': '🏢 Organizations',
                    'GPE': '🌍 Locations',
                    'DATE': '📅 Dates'
                }
                
                for label, items in entities.items():
                    if items:
                        with st.expander(f"{entity_types.get(label, label)}"):
                            for item in items:
                                st.write(f"• {item}")
                
                # WORDCLOUD OF SKILLS
                if skills:
                    st.subheader("Skills Word Cloud")
                    try:
                        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                                             colormap='viridis', max_words=100).generate(' '.join(skills))
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    except ImportError:
                        st.info("Install wordcloud and matplotlib packages to see skills word cloud visualization")
            
            with export_tab:
                st.subheader("Export Parsed Data")
                
                # prep data for export
                parsed_data = {
                    "contact_info": contact_info,
                    "summary": summary,
                    "skills": skills,
                    "experience": experiences,
                    "education": education,
                    "certifications": certifications
                }
                
                # create downloadable JSON
                create_downloadable_json(parsed_data)
                
                # display as tables
                st.subheader("Skills")
                if skills:
                    skills_df = pd.DataFrame({"Skill": skills})
                    st.dataframe(skills_df)
                
                st.subheader("Education")
                if education:
                    education_df = pd.DataFrame(education)
                    st.dataframe(education_df)
                
                st.subheader("Experience")
                if experiences:
                    # simplify experience data for table display
                    exp_data = []
                    for exp in formatted_experiences:
                        exp_data.append({
                            "Title": exp["title"],
                            "Project": exp["project"],
                            "Technologies": ", ".join(exp["technologies"])
                        })
                    exp_df = pd.DataFrame(exp_data)
                    st.dataframe(exp_df)
        else:
            st.error("Failed to extract text from the uploaded PDF. Please try a different file or format.")
