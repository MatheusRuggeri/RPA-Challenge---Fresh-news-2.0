# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:14:28 2024

@author: JoaoMurdiga
"""

import re

def make_valid_filename(filename):
    # Define a regular expression for invalid characters on Windows
    pattern = r'[<>:"/\\|?*]'
    # Replace invalid characters with an underscore
    valid_filename = re.sub(pattern, '_', filename)
    return valid_filename

test_list = [
    "test:invalid*file?name.jpg",
    "<invalid>file.png",
    "valid_filename.jpeg",
    "my@email.com",
    "!special#chars$.jpg",
    "with spaces.bmp",
    "with_underscores.tiff",
    "with-dashes.gif",
    "with.periods.jpg",
    "with_1234567890.bmp",
    "with_CASE.jpg",
    "with_unicode_æøå.jpg",
    "with_unicode_中文字符.jpg",
    "with;semi;colon.jpg",
    "with,comma.jpg",
    "with:colon.jpg",
    "with\"quotation\".jpg",
    "with*asterisk.jpg",
    "with?question.jpg"
]

for filename in test_list:
    valid_filename = make_valid_filename(filename)
    if (filename == valid_filename):
        print(f'File: "{filename}"\n')
    
    else:
        print(f'File: "{filename}"')
        print(f'\t\t-> "{valid_filename}"')
