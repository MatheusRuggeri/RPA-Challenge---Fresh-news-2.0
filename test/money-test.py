# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:14:28 2024

@author: JoaoMurdiga
"""

import re

def has_money_in_text(text):
    # Define regular expression patterns for different money formats
    patterns = [
        re.compile(r'\$\d{1,3}(,\d{3})*(\.\d{1,2})?', re.IGNORECASE),  # $11.1 or $111,111.11 -> '$' + '1-3 digits' + ',' + '1-3 digits' + '.' + '1-2 digits'
        re.compile(r'\d+ dollars', re.IGNORECASE),                     # 11 dollars
        re.compile(r'\d+ USD', re.IGNORECASE)                          # 11 USD
    ]
    
    # Check if any pattern matches
    for pattern in patterns:
        if pattern.search(text):
            return True

# Test the function with numbers and potential currency identifiers
test_texts = [
    "$11.1",
    "$111,111.11",
    "11 dollars",
    "11 USD",
    "1000",
    "$12",
    "$1,234.56",
    "$1234567.89",
    "$100,000",
    "$0.99",
    "5000",
    "100 USD",
    "100 Usd",
    "100 usd",
    "6000 dollars",
    "6000 Dollars",
    "6000 DoLLars",
    "12345 USD",
    "$999,999",
    "11USD",
    "$100,00",
    "$0.01",
    "10dollars",
    "1,000,000 dollars"
]

for text in test_texts:
    result = has_money_in_text(text)
    print(f'Text: "{text}"')
    if (result == True):
        print(f'\t\t-> {result}')
    else:
        print('')