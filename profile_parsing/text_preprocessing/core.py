import spacy
from typing import List, Tuple
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk

nlp = spacy.load("en_core_web_sm")

# enhanced stopwords
custom_stopwords = set(stopwords.words('english'))
custom_stopwords.update({
    'project', 'developer', 'developed', 'system', 'used', 'responsible', 'worked',
    'experience', 'application', 'platform', 'management', 'team', 'develop', 'tools',
    'frontend', 'backend', 'based', 'and', 'with', 'for', 'to', 'the', 'on', 'a', 'of'
})

stemmer = PorterStemmer()

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

def extract_key_phrases(tokens: List[str]) -> List[str]:
    """
    extracts meaningful multiword expressions and phrases from the tokens
    """
    doc = nlp(" ".join(tokens))
    key_phrases = set()

    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        # only keep meaningful phrases liek more than one word, not too long
        if ' ' in phrase and len(phrase) < 50:
            key_phrases.add(phrase)

    return list(key_phrases)

def get_pos_tags(text: str) -> List[Tuple[str, str]]:
    """
    extracts parts of speech tags from a given text
    """
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]

def stem_tokens(tokens: List[str]) -> List[str]:
    """
    stems a list of tokens
    """
    return [stemmer.stem(token) for token in tokens]
