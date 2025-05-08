import re 
from typing import List, Dict
from .skills_extractor import extract_skills

def extract_experience(text: str) -> List[Dict[str, str]]:
    """
    extracts the experience details and project from the given resume text
    
    for now, this is specific for the format of our sample resumes
    """
    experience = []

    projects_section_pattern = r'(?:PROJECTS\s*&\s*EXPERIENCE|EXPERIENCE|PROJECTS)([\s\S]+?)(?=SKILLS|EDUCATION|\Z)'
    projects_section = re.search(projects_section_pattern, text, re.IGNORECASE)
    
    if projects_section:
        projects_text = projects_section.group(1)
    else:
        # look for development sections directly
        dev_section_pattern = r'(Mobile|Web)\s+Development([\s\S]+?)(?=Mobile|Web|SKILLS|EDUCATION|\Z)'
        dev_sections = list(re.finditer(dev_section_pattern, text, re.IGNORECASE))
        
        if dev_sections:
            projects_text = ""
            for section in dev_sections:
                projects_text += section.group(0) + "\n\n"
        else:
            projects_text = text
    
    # first look for dev sections
    dev_section_pattern = r'(Mobile|Web)\s+Development([\s\S]+?)(?=Mobile|Web|SKILLS|EDUCATION|\Z)'
    dev_sections = list(re.finditer(dev_section_pattern, projects_text, re.IGNORECASE))
    
    if dev_sections:
        for section in dev_sections:
            dev_type = section.group(1)  # mobile or Web
            section_text = section.group(2)

            # pattern for project entries in the format:
            # project Name: - role
            # description...
            project_entries = re.split(r'\n(?=[A-Z][^:\n]+(?::|-))', section_text)

            for entry in project_entries:
                if not entry.strip():
                    continue

                # try to extract project name and role
                project_role_match = re.match(r'([^-:]+)(?:\s*:\s*)?(?:\s*-\s*)?([^-\n]+)?', entry)

                if project_role_match:
                    project_name = project_role_match.group(1).strip() if project_role_match.group(1) else ""
                    role = project_role_match.group(2).strip() if project_role_match.group(2) else ""
                
                # get description (everything after the first line)
                description_lines = entry.split('\n')[1:]
                description = '\n'.join(description_lines).strip()

                tech_used = extract_skills(entry) # extract technologies used

                experience.append({
                    'title': role if role else "Developer",
                    'project': project_name,
                    'type': dev_type,
                    'technologies': tech_used,
                    'description': description if description else entry.strip()
                })

    # if no proj found using dev sections, try a more gen approach
    if not experience:
        # l for lines that might be project titles (ending with Developer, Designer, etc.)
        role_keywords = ['developer', 'designer', 'analyst', 'engineer', 'manager']
        lines = projects_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # check is tsis line looks like a proj title with role
            if line and any(keyword.lower() in line.lower() for keyword in role_keywords):
                # try to extract proj name and role
                project_role_match = re.match(r'([^-:]+)(?:\s*:\s*)?(?:\s*-\s*)?([^-\n]+)?', line)
                
                if project_role_match:
                    project_name = project_role_match.group(1).strip() if project_role_match.group(1) else ""
                    role = project_role_match.group(2).strip() if project_role_match.group(2) else ""

                    # collect description liens until we hit anotehr potential proj title
                    description_lines = []
                    j = i + 1
                    while j < len(lines) and not any(keyword.lower() in lines[j].lower() for keyword in role_keywords):
                        description_lines.append(lines[j])
                        j += 1 

                    description = '\n'.join(description_lines).strip()

                    tech_used = extract_skills(description)

                    experience.append({
                        'title': role if role else "Developer",
                        'project': project_name,
                        'technologies': tech_used,
                        'description': description
                    })

                    i = j - 1  # skip to the end of the project description
        i += 1
    
    # if still no projects found, look for specific proj names from our sample
    if not experience:
        project_names = [
            "BudgetBuddy", 
            "Hotel's Property Management System", 
            "Library Book Borrow Management System",
            "Hotel Management System",
            "Dental Scheduling System",
            "GenKind",
            "Inventory Management System",
            "Vendor Management System"
        ]

        for project_name in project_names:
            project_pattern = f"{re.escape(project_name)}(.*?)(?=BudgetBuddy|Hotel's Property|Library Book|Hotel Management|Dental Scheduling System|GenKind|Inventory Management System|Vendor Management System |\Z)"
            project_match = re.search(project_pattern, text, re.DOTALL)
            
            if project_match:
                project_text = project_name + project_match.group(1)

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

