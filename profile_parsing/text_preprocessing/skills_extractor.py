import re 
import os
from typing import List, Set

def load_skill_keywords() -> Set[str]:
    '''
    loads skill keywords from the external file
    '''
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        skill_file_path = os.path.join(current_dir, 'data', 'skill_keywords.txt')

        if os.path.exists(skill_file_path):
            with open(skill_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                skill_set_str = content.split('=', 1)[1].strip()
                skill_keywords = eval(skill_set_str)
                return skill_keywords
        else:
            print(f"Warning: Skill keywords file not found at {skill_file_path}")
            return default_skill_keywords()
    except Exception as e:
        print(f"Error loading skill keywords: {e}")
        return default_skill_keywords()
    
def default_skill_keywords() -> Set[str]:
    """
    Returns the default set of skill keywords as a fallback
    """
    return {
        # Programming Languages
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
        'typescript', 'scala', 'perl', 'r', 'matlab', 'dart', 'objective-c', 'vba', 'powershell',
        'bash', 'shell', 'groovy', 'lua', 'haskell', 'clojure', 'elixir', 'erlang', 'fortran',
        
        # Web Development
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'jquery', 'react', 'angular', 'vue',
        'node.js', 'express', 'django', 'flask', 'spring', 'asp.net', 'laravel', 'symfony', 'rails',
        'gatsby', 'next.js', 'nuxt.js', 'svelte', 'ember', 'backbone', 'webpack', 'gulp', 'grunt',
        'babel', 'graphql', 'rest api', 'soap', 'json', 'xml', 'ajax', 'pwa', 'responsive design',
        'mvc', 'winforms',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova', 'swift ui',
        'jetpack compose', 'kotlin multiplatform', 'flutterflow',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql server', 'mssql', 'nosql',
        'redis', 'cassandra', 'dynamodb', 'firebase', 'elasticsearch', 'neo4j', 'mariadb', 'couchdb',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',
        'ansible', 'chef', 'puppet', 'prometheus', 'grafana', 'elk stack', 'serverless', 'lambda',
        'heroku', 'netlify', 'vercel', 'digitalocean', 'linode',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'ai', 'artificial intelligence', 'data science',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib',
        'seaborn', 'tableau', 'power bi', 'data visualization', 'nlp', 'computer vision',
        'reinforcement learning', 'big data', 'hadoop', 'spark', 'data mining', 'statistics',
        
        # Version Control
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
        
        # Design & UI/UX
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'indesign', 'ui design',
        'ux design', 'wireframing', 'prototyping', 'user research', 'canva',
        
        # Project Management & Methodologies
        'agile', 'scrum', 'kanban', 'waterfall', 'jira', 'trello', 'asana', 'confluence', 'lean',
        'prince2', 'pmp', 'itil',
        
        # Testing & QA
        'unit testing', 'integration testing', 'selenium', 'jest', 'mocha', 'cypress', 'junit',
        'pytest', 'testng', 'qunit', 'jasmine', 'karma', 'postman', 'swagger', 'tdd', 'bdd',
        
        # Desktop & GUI
        'wpf', 'winforms', 'qt', 'gtk', 'javafx', 'electron', 'tkinter', 'wxpython', 'pyqt',
        
        # IDEs & Tools
        'visual studio', 'visual studio code', 'intellij', 'pycharm', 'eclipse', 'android studio',
        'xcode', 'sublime text', 'atom', 'vim', 'emacs',
        
        # Other
        'blockchain', 'cryptocurrency', 'iot', 'embedded systems', 'game development', 'unity',
        'unreal engine', 'ar', 'vr', 'cybersecurity', 'networking', 'seo', 'digital marketing',
        'low-code', 'no-code'
    }

# load the skill keywords
SKILL_KEYWORDS = load_skill_keywords()

def extract_skills(text: str) -> List[str]:
    '''
    extracts skills from the resume text using a comprehenxive skill db and context-aware matching
    '''
    found_skills = set()
    text_lower = text.lower()

    # look for skills section first
    skill_section_pattern = r'(?:SKILLS|TECHNICAL SKILLS|EXPERTISE|COMPETENCIES|TECHNOLOGIES)(?::|.{0,10})\s*([\s\S]+?)(?:\n\s*\n|\n[A-Z]|\Z)'
    skill_section = re.search(skill_section_pattern, text_lower, re.IGNORECASE)

    if skill_section:
        skill_text = skill_section.group(1)
        #process hte skills section specifically 
        # handle skills in paragrpah format
        if ',' in skill_text or '-' in skill_text:
            # split by common separators
            potential_skills = re.split(r'[,\-•|&/]', skill_text)
            for item in potential_skills:
                item = item.strip().lower()
                if item and len(item) > 2: # avoid empty or short strings
                    for skill in SKILL_KEYWORDS:
                        if re.search(r'\b' + re.escape(skill) + r'\b', item):
                            found_skills.add(skill)
        else:
            # handle skills in list format
            lines = skill_text.split('\n')
            for line in lines:
                line = line.strip().lower()
                if line and len(line) > 2:
                    for skill in SKILL_KEYWORDS:
                        if re.search(r'\b' + re.escape(skill) + r'\b', line):
                            found_skills.add(skill)

    # direct skill matching throughout the text
    for skill in SKILL_KEYWORDS:
        # use word boundary to avoid partial matches 
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    # process skills for better display
    processed_skills = []
    for skill in found_skills:
        # capitalize 
        if skill.lower() in ['html', 'css', 'php', 'sql', 'api', 'aws', 'gcp', 'ui', 'ux', 'mvc']:
            processed_skills.append(skill.upper())
        elif skill.lower() in ['asp.net', 'c#', 'ms sql']:
            processed_skills.append(skill.upper())
        elif '.' in skill:  # keep dots for things like node.js
            processed_skills.append(skill)
        else:
            processed_skills.append(skill.title())
    
    return sorted(processed_skills)
