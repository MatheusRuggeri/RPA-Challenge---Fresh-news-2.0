# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:14:28 2024

@author: JoaoMurdiga
"""

import re

def count_name_in_text(text, name):
    pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
    matches = pattern.findall(text)
    return len(matches)

# Test the function with modified short texts
test_texts = [
    "Matheus and Alex are friends.",
    "MATHEUS likes to do RPAs.",
    "Matheus loves programming, matheus also enjoys cycling.",
    "Matthew.",
    "Sometimes, people call me math.",
    "AMatheusZ should not be a match.",
]

name_to_search = "Matheus"

for text in test_texts:
    count = count_name_in_text(text, name_to_search)
    print(f'Text: "{text}"')
    print(f'\t\t-> {count}')
