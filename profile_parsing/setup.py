# this could be migrated to the main directory to set up the whole project later on , 
# for now it's just here for profile parsing and texr analysis module

import subprocess
import sys

def install_dependencies():
    '''install required packages for this MPMS module'''
    print("installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("downloading spaCy model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    
    print("downloading NLTK data...")
    import nltk
    nltk.download('stopwords')
    
    print("setup complete!")

if __name__ == "__main__":
    install_dependencies()
