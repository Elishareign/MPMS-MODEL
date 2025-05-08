import re
from typing import List, Dict

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    extracts education info from resume text
    """
    education = []
    
    # look for educ section first
    education_section_pattern = r'EDUCATION([\s\S]+?)(?=PROJECTS|EXPERIENCE|SKILLS|\Z)'
    education_section = re.search(education_section_pattern, text, re.IGNORECASE)

    if education_section:
        education_text = education_section.group(1)
    else:
        # try to find educ entries without a section header
        education_text = text
    
    # pattern specifcally for the format used sa sample cv
    # level (yr ramge), school - additional ingo
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
    
    # if no matches found with the specific pattern, try am ore general approach
    if not education:
        edu_keywords = ['high school', 'college', 'university', 'institute', 'bachelor', 'master', 'phd']
        lines = education_text.split('\n')
        
        current_edu = {}
        for i, line in enumerate(lines):
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in edu_keywords):
                # if building a previoud entry, save it
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
                
                current_edu = { 'level': level, 'school': "", 'year': year, 'additional': ""}

                # check if next line contains school info\
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(keyword in next_line.lower() for keyword in edu_keywords):
                    # like the school line
                        school_parths = next_line.split('-', 1)
                        current_edu['school'] = school_parths[0].strip()
                        if len(school_parths) > 1:
                            current_edu['additional'] = school_parths[1].strip()
       
        # add the last education entry
        if current_edu and 'level' in current_edu:
            education.append(current_edu)

    return education
