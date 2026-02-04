#!/bin/bash
# Test script to verify mapper and reducer work correctly locally

echo "========================================="
echo "Testing MapReduce Scripts Locally"
echo "========================================="

# Create sample input
echo "Creating sample input..."
cat > sample_input.txt << EOF
Hello world hello
The quick brown fox jumps over the lazy dog
Hello Hadoop MapReduce on Amazon EMR
Distributed systems are powerful systems
The MapReduce programming model is elegant
EOF

echo -e "\n--- Sample Input ---"
cat sample_input.txt

echo -e "\n--- Testing Mapper ---"
cat sample_input.txt | python3 mapper.py

echo -e "\n--- Testing Full Pipeline (Mapper -> Sort -> Reducer) ---"
cat sample_input.txt | python3 mapper.py | sort | python3 reducer.py

echo -e "\n--- Top 10 Most Frequent Words ---"
cat sample_input.txt | python3 mapper.py | sort | python3 reducer.py | sort -t$'\t' -k2 -nr | head -10

echo -e "\n========================================="
echo "Test completed successfully!"
echo "========================================="
