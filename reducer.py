#!/usr/bin/env python3
"""
Reducer script for Word Count MapReduce job
Reads (word, count) pairs from stdin, aggregates counts per word
"""
import sys
from collections import defaultdict

def main():
    word_counts = defaultdict(int)
    
    # Read from standard input
    for line in sys.stdin:
        line = line.strip()
        
        # Parse the key-value pair
        try:
            word, count = line.split('\t', 1)
            word_counts[word] += int(count)
        except ValueError:
            # Skip malformed lines
            continue
    
    # Emit final counts
    for word, count in sorted(word_counts.items()):
        print(f"{word}\t{count}")

if __name__ == "__main__":
    main()
