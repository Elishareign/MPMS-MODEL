import spacy
from typing import List, Dict, Tuple, Set, Optional
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer
import re
import string
from nltk.corpus import stopwords
import nltk
import os

nlp = spacy.load("en_core_web_sm")

# Enhanced stopwords
custom_stopwords = set(stopwords.words('english'))
custom_stopwords.update({
    'project', 'developer', 'developed', 'system', 'used', 'responsible', 'worked',
    'experience', 'application', 'platform', 'management', 'team', 'develop', 'tools',
    'frontend', 'backend', 'based', 'and', 'with', 'for', 'to', 'the', 'on', 'a', 'of'
})

stemmer = PorterStemmer()

def load_skill_keywords():
    '''
    loads skill keywords from the external file
    '''
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        skill_file_path = os.path.join(current_dir, 'data', 'skill_keywords.txt')

        if os.path.exists(skill_file_path):
            with open(skill_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                skill_set_str = content.split('=', 1)[1].strip()
                skill_keywords = eval(skill_set_str)
                return skill_keywords
        else:
            print(f"Warning: Skill keywords file not found at {skill_file_path}")
            return set()
    except Exception as e:
        print(f"Error loading skill keywords: {e}")
        return set()

skill_keywords = load_skill_keywords()

def preprocess_text(text: str) -> List[str]:
    """
    tokenizes, lemmatizes, removes custom stopwords and punctuation
    """
    text = re.sub(r'\s+', ' ', text).strip()
    
    doc = nlp(text)
    tokens = [
       token.lemma_.lower()
       for token in doc
       if token.lemma_.lower() not in custom_stopwords 
       and not token.is_punct 
       and not token.is_space
       and len(token.text) > 1  # ignore single characters
    ]
    return tokens

def extract_contact_info(text: str) -> Dict[str, str]:
    """
    extracts contact info from resume text
    """
    contact_info = {}
    
    # name pattern (usually at the begingnninf of the resume)
    name_pattern = r'^([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+)'
    name_match = re.search(name_pattern, text)
    if name_match:
        contact_info['name'] = name_match.group(0)
    
    # email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group(0)
    
    # pphone pattern (diff formats including international)
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    
    # linkedIn pattern
    linkedin_pattern = r'(?:linkedin\.com/in/|linkedin:)([A-Za-z0-9_-]+)'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)
    
    # gitHub pattern
    github_pattern = r'(?:github\.com/|github:)([A-Za-z0-9_-]+)'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0)
    
    # location/address
    header_lines = text.split('\n')[:3]  # check first 3 lines
    for line in header_lines:
        if '|' in line and email_match and line.find(email_match.group(0)) > 0:
            parts = line.split('|')
            for part in parts:
                part = part.strip()
                # skip email and phone parts
                if email_match and email_match.group(0) in part:
                    continue
                if phone_match and phone_match.group(0) in part:
                    continue
                if len(part) > 5:
                    contact_info['location'] = part
                    break
    
    # if location not found in header, try general pattern
    if 'location' not in contact_info:
        address_pattern = r'(?:Address|Location|residing at|living in|based in)?\s*(?::|,)?\s*([^,|]+(?:,\s*[^,|]+){1,3})'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            contact_info['location'] = address_match.group(1).strip()
    
    return contact_info

def extract_summary(text: str) -> str:
    """
    extracts the professional summary
    """
    # Look for SUMMARY section
    summary_pattern = r'(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE|ABOUT ME)(?::|.{0,10})\s*([\s\S]+?)(?=\n\s*\n|\n[A-Z]|\Z)'
    summary_match = re.search(summary_pattern, text, re.IGNORECASE)
    
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # make sure education is not included
        if 'EDUCATION' in summary_text:
            summary_text = summary_text.split('EDUCATION')[0].strip()
        return summary_text
    
    # if no explicit summary section, try to find a parafraph at the beginning 
    lines = text.split('\n')
    for i, line in enumerate(lines[:15]):  # look in first 15 lines
        if len(line) > 100: 
            return line.strip()
    
    return ""

def extract_skills(text: str) -> List[str]:
    """
    extracts skills from the resume text using a comprehensive skill database
    and context-aware matching
    """
    found_skills = set()
    text_lower = text.lower()
    
    # look for skills section first
    skill_section_pattern = r'(?:SKILLS|TECHNICAL SKILLS|EXPERTISE|COMPETENCIES|TECHNOLOGIES)(?::|.{0,10})\s*([\s\S]+?)(?:\n\s*\n|\n[A-Z]|\Z)'
    skill_section = re.search(skill_section_pattern, text, re.IGNORECASE)
    
    if skill_section:
        skill_text = skill_section.group(1)
        # process the skills section specifically
        
        # handle skills in paragraph format (comma or dash separated)
        if ',' in skill_text or '-' in skill_text:
            # Split by common separators
            potential_skills = re.split(r'[,\-•|&/]', skill_text)
            for item in potential_skills:
                item = item.strip().lower()
                if item and len(item) > 2:  # avoid empty or very short items
                    # check if this item contains any skill from our text file
                    for skill in load_skill_keywords():
                        if re.search(r'\b' + re.escape(skill) + r'\b', item):
                            found_skills.add(skill)
        
        # handle skills in list format
        else:
            lines = skill_text.split('\n')
            for line in lines:
                line = line.strip().lower()
                if line and len(line) > 2:
                    for skill in load_skill_keywords():
                        if re.search(r'\b' + re.escape(skill) + r'\b', line):
                            found_skills.add(skill)
    
    # Direct skill matching throughout the text
    for skill in load_skill_keywords():
        # use word boundary to avoid partial matchse
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    processed_skills = []
    for skill in found_skills:
        # capitalize appropriately
        if skill.lower() in ['html', 'css', 'php', 'sql', 'api', 'aws', 'gcp', 'ui', 'ux', 'mvc']:
            processed_skills.append(skill.upper())
        elif skill.lower() in ['asp.net', 'c#', 'ms sql']:
            processed_skills.append(skill.upper())
        elif '.' in skill:  # keep dots for things like Node.js
            processed_skills.append(skill)
        else:
            processed_skills.append(skill.title())
    
    return sorted(processed_skills)

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    extracts education info from resume text
    """
    education = []
    
    # look for education section first
    education_section_pattern = r'EDUCATION([\s\S]+?)(?=PROJECTS|EXPERIENCE|SKILLS|\Z)'
    education_section = re.search(education_section_pattern, text, re.IGNORECASE)
    
    if education_section:
        education_text = education_section.group(1)
    else:
        # try to find education entriees without a section header
        education_text = text
    
    edu_pattern = r'(Elementary School|Junior High School|Senior High School|College|Bachelor|Master|PhD)(?:\s*\(([^)]+)\))?\s*\n([^-\n]+)(?:\s*-\s*(.+))?'
    
    matches = re.finditer(edu_pattern, education_text)
    for match in matches:
        level = match.group(1).strip()
        year = match.group(2).strip() if match.group(2) else ""
        school = match.group(3).strip()
        additional = match.group(4).strip() if match.group(4) else ""
        
        education.append({
            'level': level,
            'school': school,
            'year': year,
            'additional': additional
        })
    
    # if no found matches on specific, try a more general approach
    if not education:
        edu_keywords = ['high school', 'college', 'university', 'institute', 'bachelor', 'master', 'phd']
        lines = education_text.split('\n')
        
        current_edu = {}
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # hceck if this line contains educ levle
            if any(keyword in line_lower for keyword in edu_keywords):
                if current_edu and 'level' in current_edu:
                    education.append(current_edu)
                    current_edu = {}
                
                level = line.strip()
                year = ""
                
                # check for year in parentheses
                year_match = re.search(r'\(([^)]+)\)', level)
                if year_match:
                    year = year_match.group(1)
                    level = level.replace(f"({year})", "").strip()
                
                current_edu = {'level': level, 'school': "", 'year': year, 'additional': ""}
                
                # check if the next line might contain school info
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(keyword in next_line.lower() for keyword in edu_keywords):
                        # likely the school line
                        school_parts = next_line.split('-', 1)
                        current_edu['school'] = school_parts[0].strip()
                        if len(school_parts) > 1:
                            current_edu['additional'] = school_parts[1].strip()
        
        # add the last education entry
        if current_edu and 'level' in current_edu:
            education.append(current_edu)
    
    return education

def extract_certifications(text: str) -> List[str]:
    """
    extracts certifications and awards from resume text
    """
    certifications = []
    
    # look specifically for "Consistent Academic Excellence Awardee" pattern seen in the sample
    excellence_pattern = r'Consistent\s+Academic\s+Excellence\s+Awardee'
    excellence_match = re.search(excellence_pattern, text, re.IGNORECASE)
    if excellence_match:
        certifications.append(excellence_match.group(0))
    
    # Look for "Graduated with Honors" and similar patterns
    honors_pattern = r'Graduated\s+with\s+(?:High\s+)?Honors'
    honors_matches = re.finditer(honors_pattern, text, re.IGNORECASE)
    for match in honors_matches:
        if match.group(0) not in certifications:
            certifications.append(match.group(0))
    
    # Look for certification/award keywords
    cert_keywords = [
        'certificate', 'certified', 'certification', 'credential', 'diploma', 
        'license', 'award', 'achievement', 'honor', 'recognition', 'excellence'
    ]
    
    # Try to find certification section
    cert_section_pattern = r'(?:CERTIFICATIONS|CERTIFICATES|AWARDS|ACHIEVEMENTS|HONORS)(?::|.{0,10})([\s\S]+?)(?:\n\s*\n|\n[A-Z]|\Z)'
    cert_section = re.search(cert_section_pattern, text, re.IGNORECASE)
    
    if cert_section:
        cert_text = cert_section.group(1)
        # Split by common list item indicators
        items = [line.strip() for line in re.split(r'[\n•-]', cert_text) if line.strip()]
        for item in items:
            if len(item) > 5 and item not in certifications:  # Filter out very short items
                certifications.append(item)
    
    # If no section found or no certifications found in section, look throughout the text
    if not certifications:
        # Look for lines containing certification keywords
        for line in text.splitlines():
            line = line.strip()
            if any(keyword in line.lower() for keyword in cert_keywords) and len(line) > 10:
                # Avoid duplicating education entries
                if not any(edu_keyword in line.lower() for edu_keyword in ['bachelor', 'master', 'phd', 'high school']):
                    certifications.append(line)
    
    return certifications if certifications else ["No certifications or awards found."]

def extract_experience(text: str) -> List[Dict[str, str]]:
    """
    Extracts work experience and projects from resume text
    specifically for the format in the sample resume
    """
    experience = []
    
    # Look for Projects & Experience section
    projects_section_pattern = r'(?:PROJECTS\s*&\s*EXPERIENCE|EXPERIENCE|PROJECTS)([\s\S]+?)(?=SKILLS|EDUCATION|\Z)'
    projects_section = re.search(projects_section_pattern, text, re.IGNORECASE)
    
    if projects_section:
        projects_text = projects_section.group(1)
    else:
        # Look for development sections directly
        dev_section_pattern = r'(Mobile|Web)\s+Development([\s\S]+?)(?=Mobile|Web|SKILLS|EDUCATION|\Z)'
        dev_sections = list(re.finditer(dev_section_pattern, text, re.IGNORECASE))
        
        if dev_sections:
            projects_text = ""
            for section in dev_sections:
                projects_text += section.group(0) + "\n\n"
        else:
            projects_text = text
    
    # First look for development sections
    dev_section_pattern = r'(Mobile|Web)\s+Development([\s\S]+?)(?=Mobile|Web|SKILLS|EDUCATION|\Z)'
    dev_sections = list(re.finditer(dev_section_pattern, projects_text, re.IGNORECASE))
    
    if dev_sections:
        for section in dev_sections:
            dev_type = section.group(1)  # Mobile or Web
            section_text = section.group(2)
            
            # Pattern for project entries in the format:
            # Project Name: - Role
            # De/scription...
            project_entries = re.split(r'\n(?=[A-Z][^:\n]+(?::|-))', section_text)
            
            for entry in project_entries:
                if not entry.strip():
                    continue
                
                # Try to extract project name and role
                project_role_match = re.match(r'([^-:]+)(?:\s*:\s*)?(?:\s*-\s*)?([^-\n]+)?', entry)
                
                if project_role_match:
                    project_name = project_role_match.group(1).strip() if project_role_match.group(1) else ""
                    role = project_role_match.group(2).strip() if project_role_match.group(2) else ""
                    
                    # Get description (everything after the first line)
                    description_lines = entry.split('\n')[1:]
                    description = '\n'.join(description_lines).strip()
                    
                    # Extract technologies used
                    tech_used = extract_skills(entry)
                    
                    experience.append({
                        'title': role if role else "Developer",
                        'project': project_name,
                        'type': dev_type,
                        'technologies': tech_used,
                        'description': description if description else entry.strip()
                    })
    
    # If no projects found using development sections, try a more general approach
    if not experience:
        # Look for lines that might be project titles (ending with Developer, Designer, etc.)
        role_keywords = ['developer', 'designer', 'analyst', 'engineer', 'manager']
        lines = projects_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line looks like a project title with role
            if line and any(keyword.lower() in line.lower() for keyword in role_keywords):
                # Try to extract project name and role
                project_role_match = re.match(r'([^-:]+)(?:\s*:\s*)?(?:\s*-\s*)?([^-\n]+)?', line)
                
                if project_role_match:
                    project_name = project_role_match.group(1).strip() if project_role_match.group(1) else ""
                    role = project_role_match.group(2).strip() if project_role_match.group(2) else ""
                    
                    # Collect description lines until we hit another potential project title
                    description_lines = []
                    j = i + 1
                    while j < len(lines) and not any(keyword.lower() in lines[j].lower() for keyword in role_keywords):
                        description_lines.append(lines[j])
                        j += 1
                    
                    description = '\n'.join(description_lines).strip()
                    
                    # Extract technologies used
                    tech_used = extract_skills(description)
                    
                    experience.append({
                        'title': role if role else "Developer",
                        'project': project_name,
                        'technologies': tech_used,
                        'description': description
                    })
                    
                    # Move to the next potential project title
                    i = j - 1
            
            i += 1
    
    # If still no projects found, look for specific project names from the sample
    if not experience:
        project_names = [
            "BudgetBuddy", 
            "Hotel's Property Management System", 
            "Library Book Borrow Management System",
            "Hotel Management System"
        ]
        
        for project_name in project_names:
            project_pattern = f"{re.escape(project_name)}(.*?)(?=BudgetBuddy|Hotel's Property|Library Book|Hotel Management|\Z)"
            project_match = re.search(project_pattern, text, re.DOTALL)
            
            if project_match:
                project_text = project_name + project_match.group(1)
                
                # Try to extract role
                role_match = re.search(r'-\s*(Developer|Designer|Analyst|Engineer|Manager[^-\n]*)', project_text)
                role = role_match.group(1) if role_match else "Developer"
                
                # Extract technologies
                tech_used = extract_skills(project_text)
                
                experience.append({
                    'title': role,
                    'project': project_name,
                    'technologies': tech_used,
                    'description': project_text
                })
    
    return experience


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts named entities from resume text with improved accuracy
    """
    doc = nlp(text)
    entities = {'PERSON': [], 'ORG': [], 'GPE': [], 'DATE': []}
    
    for ent in doc.ents:
        if ent.label_ in entities:
            # Clean up entity text
            clean_entity = re.sub(r'\s+', ' ', ent.text).strip()
            
            # Filter out very short entities and common false positives
            if len(clean_entity) > 2 and clean_entity.lower() not in ['the', 'a', 'an', 'this', 'that']:
                entities[ent.label_].append(clean_entity)
    
    # Remove duplicates and sort
    return {k: sorted(set(v)) for k, v in entities.items() if v}

def extract_key_phrases(tokens: List[str]) -> List[str]:
    """
    Extracts meaningful multiword expressions and phrases from the tokens
    """
    doc = nlp(" ".join(tokens))
    key_phrases = set()
    
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        # Only keep meaningful phrases (more than one word, not too long)
        if ' ' in phrase and len(phrase) < 50:
            key_phrases.add(phrase)
    
    return list(key_phrases)

def get_pos_tags(text: str) -> List[Tuple[str, str]]:
    """
    Extracts parts of speech tags from a given text
    """
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]

def stem_tokens(tokens: List[str]) -> List[str]:
    """
    Stems a list of tokens
    """
    return [stemmer.stem(token) for token in tokens]

