#!/usr/bin/env python3
"""
Mapper script for Word Count MapReduce job
Reads lines from stdin, splits into words, and emits (word, 1) pairs
"""
import sys
import re

def main():
    # Read from standard input
    for line in sys.stdin:
        # Remove leading/trailing whitespace and convert to lowercase
        line = line.strip().lower()
        
        # Split line into words (remove punctuation, keep alphanumeric)
        words = re.findall(r'\b[a-z0-9]+\b', line)
        
        # Emit key-value pairs: word \t 1
        for word in words:
            if word:  # Skip empty strings
                print(f"{word}\t1")

if __name__ == "__main__":
    main()
