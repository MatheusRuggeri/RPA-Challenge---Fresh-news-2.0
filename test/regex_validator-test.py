# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:14:28 2024

@author: JoaoMurdiga
"""

import re

# Define the regex patterns
patterns = [r'\$\d{1,3}(,\d{3})*(\.\d{1,2})?', r'\d+ dollars', r'\d+ USD']

# Strings to test
test_strings = [
    "$11.1",
    "$111,111.11",
    "11 dollars",
    "11 USD",
    "$111",
    "20 USD",
    "$1000",
    "$1000000",
    "$100,000",
    "$100,000.00",
    "5 dollars",
    "5 DOLLARS",
    "5 Dollars"
]

# Test each pattern
for string in test_strings:
    for pattern in patterns:
        if re.search(pattern, string, re.IGNORECASE):
            print(f"Pattern '{pattern}' matches: {string}")
            break
    else:
        print(f"No pattern matches: {string}")