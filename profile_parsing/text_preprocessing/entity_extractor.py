import spacy
import re
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    extracts named entitied with improved accuracy (kinda? hashaahah)
    """
    doc = nlp(text)
    entities = {'PERSON': [], 'ORG': [], 'GPE': [], 'DATE': []}

    for ent in doc.ents:
        if ent.label_ in entities:
            clean_entity = re.sub(r'\s+', ' ', ent.text).strip()

            # filter out very short entities and common false positives
            if len(clean_entity) > 2 and clean_entity.lower() not in ['the', 'a', 'an', 'this', 'that']:
                entities[ent.label_].append(clean_entity)
    
    # remove duplicates and sort
    return {k: sorted(set(v)) for k, v in entities.items() if v}
