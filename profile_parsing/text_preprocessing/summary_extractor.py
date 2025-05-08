import re

def extract_summary(text: str) -> str:
    """
    extracts the professional summary 
    """
    # look for r SUMMARY section
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
    for i, line in enumerate(lines[:10]): # look in first 10 lines
        if len(line) > 100:
            return line.strip()
    
    return ""
