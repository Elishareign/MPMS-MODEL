import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
import pandas as pd

# Load NLP and sentence transformer model for semantic comparison
nlp = spacy.load("en_core_web_md")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define concept lists for matching and categorization
skills_list = ["python", "sql", "machine learning", "data analysis", "public speaking", "project management"]
roles_list = ["data scientist", "product manager", "software engineer", "data analyst", "marketing specialist"]
industries_list = ["finance", "healthcare", "tech", "startups", "e-commerce", "IT industry"]
certifications_list = ["mba", "data science certification", "machine learning certification", "certification"]

# Text preprocessor
def preprocess_text(text):
    text = text.lower()
    doc = nlp(text)
    tokens = [token for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(token.lemma_ for token in tokens)

# Parse token
def parse_tokens(text, nlp):
    doc = nlp(text)
    tokens_data = []

    # Filter by parts of speech
    relevant_pos = {"NOUN", "PROPN", "VERB"}  

    for token in doc:
        if (
            not token.is_stop
            and not token.is_punct
            and token.pos_ in relevant_pos
            and len(token.text.strip()) > 2  
        ):
            tokens_data.append({
                "Text": token.text,
                "Lemma": token.lemma_,
                "POS": token.pos_,
                "Dependency": token.dep_
            })

    return pd.DataFrame(tokens_data)

# Extract and categorize matched key phrases from input text
def extract_and_categorize_key_phrases(text):
    doc = nlp(text.lower())
    matcher = PhraseMatcher(nlp.vocab)

    all_terms = skills_list + roles_list + industries_list + certifications_list
    patterns = [nlp.make_doc(term.lower()) for term in all_terms]
    matcher.add("KEY_PHRASES", patterns)

    # Ignore generic or overly common phrases
    ignore_list = {"team", "project", "experience", "responsible"}  

    matches = matcher(doc)
    categorized = {
        "skills": [],
        "roles": [],
        "industries": [],
        "certifications": []
    }

    for _, start, end in matches:
        phrase = doc[start:end].text
        if phrase in ignore_list:
            continue
        # Categorize matched phrase
        if phrase in skills_list:
            categorized["skills"].append(phrase)
        elif phrase in roles_list:
            categorized["roles"].append(phrase)
        elif phrase in industries_list:
            categorized["industries"].append(phrase)
        elif phrase in certifications_list:
            categorized["certifications"].append(phrase)

    return categorized

# semantic match using bert
def get_semantic_matches(student_phrases, mentor_text, top_n=5, threshold=0.8):
    mentor_doc = nlp(mentor_text)

    # Extract clean and relevant noun phrases from mentor text
    mentor_chunks = list(set([
        chunk.text.strip()
        for chunk in mentor_doc.noun_chunks
        if 2 < len(chunk.text.strip()) < 50 and not chunk.root.is_stop and not chunk.root.is_punct
    ]))

    if not student_phrases or not mentor_chunks:
        return []

    # Encode student and mentor phrases into embeddings
    student_embeddings = model.encode(student_phrases, convert_to_tensor=True)
    mentor_embeddings = model.encode(mentor_chunks, convert_to_tensor=True)

    # Compute cosine similarity between student and mentor phrases
    cosine_scores = util.pytorch_cos_sim(student_embeddings, mentor_embeddings)

    matches = []
    seen_student_phrases = set()

    # For each student phrase, find the best matching mentor phrase
    for i, student_phrase in enumerate(student_phrases):
        best_score = 0.0
        best_match = None

        for j, mentor_phrase in enumerate(mentor_chunks):
            score = cosine_scores[i][j].item()
            if score > best_score:
                best_score = score
                best_match = mentor_phrase
        # Only include matches that meet the similarity threshold = 0.9
        if best_score >= threshold and student_phrase not in seen_student_phrases:
            matches.append((student_phrase, best_match, round(best_score, 2)))
            seen_student_phrases.add(student_phrase)

    return sorted(matches, key=lambda x: -x[2])[:top_n]

# Vector similarity using spaCy 
def calculate_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)
