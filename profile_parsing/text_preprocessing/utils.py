import os
import re

def load_data(filename: str) -> str:
    """
    loads data filr from the data directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', filename)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        print('warning: file not found at ', file_path)
        return ""

def clean_text(text: str) -> str:
    '''
    perfoms basic multiple spaces with single space
    '''
    text = re.sub(r'\s+', ' ', text) # replace mulptle spaces wih single space
    text = re.sub(r' \n', '\n', text) #remoce spaces before new line
    text = re.sub(r'\n+', '\n', text) # replace multiple new lines with single new line
    return text.strip()
