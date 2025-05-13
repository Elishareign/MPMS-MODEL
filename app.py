import streamlit as st
from pdf_extractor import extract_text_from_pdfs
from text_processing import (
    skills_list,
    roles_list,
    preprocess_text,
    extract_and_categorize_key_phrases,
    calculate_similarity,
    get_semantic_matches,
    parse_tokens,
    nlp
)

# Load PDF text from folders
@st.cache_data
def load_profiles(folder):
    path = f"Data/{folder}"
    return extract_text_from_pdfs(path)

# App Title
st.title("Instuctor-Student Profile Matcher")

# Load mentor profiles (from PDF)
mentor_profiles = load_profiles("Mentor")

# Tabs
tab1, tab2, tab3 = st.tabs(["Student Preferences", "Instructor Profiles", "Match Results"])

#TAB 1: Student Preferences 
with tab1:
    st.subheader("Select Your Preferred Skills and Roles")

    selected_student = st.text_input("Enter Student Name")

    if selected_student:
        # Multi-select widgets for selecting preferred skills and roles
        selected_skills = st.multiselect(
            "Select desired skills:",
            options=skills_list,
            key=f"{selected_student}_skills"
        )

        selected_roles = st.multiselect(
            "Select desired roles:",
            options=roles_list,
            key=f"{selected_student}_roles"
        )
        # Store the selected options in session state
        st.session_state[f"{selected_student}_selected_skills"] = selected_skills
        st.session_state[f"{selected_student}_selected_roles"] = selected_roles
    else:
        st.warning("Please enter a student name.")

#TAB 2: Mentor Profiles
with tab2:
    st.subheader("Instructor Profile Text & Key Phrases")

    # Loop through each mentor profile
    for filename, text in mentor_profiles.items():
        with st.expander(f"Mentor: {filename}"):
            st.text_area("Extracted Text", text, height=300)

            # Preprocess the text
            preprocessed_text = preprocess_text(text)
            st.text_area("Preprocessed Text", preprocessed_text, height=200)

            # Show parsed tokens
            df = parse_tokens(text, nlp)  
            st.markdown("### Parsed Token Table")
            st.dataframe(df)

            # Extract and categorize keywords
            categorized = extract_and_categorize_key_phrases(text)
            st.markdown("### Extracted Key Phrases")
            for category, phrases in categorized.items():
                if phrases:
                    st.markdown(f"**{category.capitalize()}**: {', '.join(set(phrases))}")
                else:
                    st.markdown(f"**{category.capitalize()}**: _None found_")

# TAB 3: Match Results
with tab3:
    st.subheader("Match Student with Mentors")

    if not selected_student:
        st.warning("Please enter a student name in Tab 1.")
    else:
        # Retrieve selected preferences from session
        selected_skills = st.session_state.get(f"{selected_student}_selected_skills", [])
        selected_roles = st.session_state.get(f"{selected_student}_selected_roles", [])

        if not selected_skills and not selected_roles:
            st.warning("Please select at least one skill or role in Tab 1.")
        else:
            # Combine skills and roles into a single set
            desired_phrases = set(selected_skills + selected_roles)
            results = []

            # Weights for scoring
            alpha = 0.5  # Phrase match weight
            beta = 0.5   # Semantic match weight

            # Loop through all mentors
            for mentor_name, mentor_text in mentor_profiles.items():
                categorized = extract_and_categorize_key_phrases(mentor_text)
                mentor_phrases = set(categorized["skills"] + categorized["roles"])

               # Jaccard similarity = (common / union of both sets)
                common = desired_phrases.intersection(mentor_phrases)
                union = desired_phrases.union(mentor_phrases)
                match_score = len(common) / len(desired_phrases)

                # Vector-based similarity using embeddings
                sim_score = calculate_similarity(" ".join(desired_phrases), mentor_text)

                # Combined score
                combined_score = alpha * match_score + beta * sim_score

                results.append((mentor_name, match_score, sim_score, common, combined_score))

            # Sort by combined score
            results.sort(key=lambda x: x[4], reverse=True)

            # Display Results
            for mentor_name, match_score, sim_score, common_phrases, combined_score in results:
                with st.expander(f"{mentor_name} — Combined Score: {combined_score * 100:.0f}%"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Phrase Match Score", f"{match_score * 100:.0f}%")
                    col2.metric("Semantic Similarity", f"{sim_score * 100:.0f}%")
                    col3.metric("Combined Match Score", f"{combined_score * 100:.0f}%")

                    # Show matched phrases 
                    st.markdown("**Matched Phrases**:")
                    if common_phrases:
                        for phrase in common_phrases:
                            st.markdown(f"- ✅ `{phrase}`")
                    else:
                        st.write("_None_")

                    #Semantic similarity
                    st.markdown("### Semantic Word Matches")
                    st.caption("Some phrases may match exactly (in phrase score) but not appear in semantic matches if they don't meet the similarity threshold.")
                    semantic_matches = get_semantic_matches(list(desired_phrases), mentor_text)
                    if semantic_matches:
                        for student_word, matched_word, score in semantic_matches:
                            st.markdown(f"- `{student_word}` ↔ `{matched_word}` (Similarity: **{score}**)")
                    else:
                        st.write("No strong semantic matches found.")
