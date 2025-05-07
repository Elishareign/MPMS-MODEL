import re
from typing import Dict

def extract_contact_info(text: str) -> Dict[str, str]:
    """
    extracts the contact infor from the given resume text
    """
    contact_info = {}

    # name pattern, usually at the begingnninf of the resume\
    name_pattern = r'^([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+)'
    name_match = re.search(name_pattern, text)
    if name_match:
        contact_info['name'] = name_match.group(0)

    # email patterm
    email_pattern =r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group(0)
    
    # phone pattern
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    
    # linkedin pattern
    linkedin_pattern = r'(?:linkedin\.com/in/|linkedin:)([A-Za-z0-9_-]+)'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)
    
    # github pattern
    github_pattern = r'(?:github\.com/|github:)([A-Za-z0-9_-]+)'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0)

    # location/address
    # first look for the pipe-separated format in the header
    header_lines = text.split('\n')[:3] # check first 3 lines
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

                if len(part) > 3:
                    contact_info['location'] = part
                    break
    
    # if loc not found in header, try general pattern
    if 'location' not in contact_info:
        address_pattern = r'(?:Address|Location|residing at|living in|based in)?\s*(?::|,)?\s*([^,|]+(?:,\s*[^,|]+){1,3})'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            contact_info['location'] = address_match.group(1).strip()
    
    return contact_info
