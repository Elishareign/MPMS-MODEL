import re
from typing import List

def extract_certifications(text: str) -> List[str]:
    """
    extracts the certs and awards from the given resume text
    """
    certifications = []

    excellence_pattern = r'Consistent\s+Academic\s+Excellence\s+Awardee'
    excellence_match = re.search(excellence_pattern, text, re.IGNORECASE)
    if excellence_match:
        certifications.append(excellence_match.group(0))

    honors_pattern = r'Graduated\s+with\s+(?:High\s+)?Honors'
    honors_matches = re.finditer(honors_pattern, text, re.IGNORECASE)
    for match in honors_matches:
        if match.group(0) not in certifications:
            certifications.append(match.group(0))

    cert_keywords = [
        'certificate', 'certified', 'certification', 'credential', 'diploma', 
        'license', 'award', 'achievement', 'honor', 'recognition', 'excellence'
    ]

    # try to find  certification section
    cert_section_pattern = r'(?:CERTIFICATIONS|CERTIFICATES|AWARDS|ACHIEVEMENTS|HONORS)(?::|.{0,10})([\s\S]+?)(?:\n\s*\n|\n[A-Z]|\Z)'
    cert_section = re.search(cert_section_pattern, text, re.IGNORECASE)

    if cert_section:
        cert_text = cert_section.group(1)
        # split by common list item indicators
        items = [line.strip() for line in re.split(r'[\n•-]', cert_text) if line.strip()]
        for item in items:
            if len(item) > 5 and item not in certifications:  # filter out very short items
                certifications.append
    
    # if no section found or no certs found in section, look throughout the text
    if not certifications:
        for line in text.splitlines():
            line = line.strip()
            if any(keyword in line.lower() for keyword in cert_keywords) and len(line) > 10:
                # avoid duplicating education entries
                if not any(edu_keyword in line.lower() for edu_keyword in ['bachelor', 'master', 'phd', 'high school']):
                    certifications.append(line)
    
    return certifications if certifications else ['No certifications or awards found']

