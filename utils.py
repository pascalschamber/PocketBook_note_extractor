import os 
from pathlib import Path

# utility functions
def get_dir_contents(base_dir, base_dir_filter=''):
    return (sorted([Path(os.path.join(base_dir, el)) for el in os.listdir(base_dir) if base_dir_filter in el]))

def clean_text(s):
    new_s = s.replace('\n', ' ')
    return new_s