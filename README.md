# Lab 5: Mini-MapReduce on Amazon EMR

## Overview
This project implements a Word Count MapReduce job on Amazon Elastic MapReduce (EMR) using Hadoop Streaming with Python.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Cluster Setup](#cluster-setup)
3. [Dataset Preparation](#dataset-preparation)
4. [MapReduce Job Execution](#mapreduce-job-execution)
5. [Experimentation](#experimentation)
6. [Output Validation](#output-validation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### AWS Academy Learner Lab
- Start your AWS Academy Learner Lab session
- Ensure you have access to EMR service
- Download the `vockey.pem` key pair from AWS Details panel

### Local Setup
```bash
# Make the key file secure
chmod 400 vockey.pem
```

---

## Cluster Setup

### Step 1: Create EMR Cluster

1. **Navigate to EMR Console**
   - Go to AWS Management Console
   - Search for "EMR" and select Elastic MapReduce

2. **Create Cluster Configuration**
   - Click "Create cluster"
   - Choose "Go to advanced options"

3. **Software Configuration**
   - Release: emr-6.x.x or latest
   - Applications: Select **Hadoop** (and optionally **Hive**)

4. **Hardware Configuration**
   - Instance type: `m4.large` (recommended for stability)
   - Number of instances:
     - Primary: 1 instance
     - Core: 1 instance (can scale to 2-4 for experiments)
     - Task: 1 instance

5. **General Cluster Settings**
   - Cluster name: `emr-mapreduce-lab5`
   - **IMPORTANT**: Uncheck "Publish cluster-specific logs to Amazon S3" to avoid bucket creation issues

6. **Security Configuration**
   - EC2 key pair: Select `vockey`
   - IAM roles:
     - Service role: `EMR_DefaultRole`
     - EC2 instance profile: `EMR_EC2_DefaultRole`

7. **Create Cluster**
   - Review and create
   - Wait 10-15 minutes for cluster to enter "Waiting" state

### Step 2: Connect to Master Node

```bash
# Get Master Public DNS from EMR cluster details
# Example: ec2-xx-xx-xx-xx.compute-1.amazonaws.com

# SSH into master node
ssh -i vockey.pem hadoop@<MASTER-PUBLIC-DNS>
```

### Step 3: Verify Cluster

```bash
# Check YARN nodes
yarn node -list

# Check HDFS health
hdfs dfsadmin -report

# Verify Hadoop version
hadoop version
```

---

## Dataset Preparation

### Step 1: Download Dataset on Master Node

```bash
# SSH into master node first
ssh -i vockey.pem hadoop@<MASTER-PUBLIC-DNS>

# Download Wikipedia corpus
wget https://github.com/LGDoor/Dump-of-Simple-English-Wiki/raw/refs/heads/master/corpus.tgz

# Verify download
ls -lh corpus.tgz

# Extract archive
tar -xvzf corpus.tgz

# Check extracted file
ls -lh corpus.txt
wc -l corpus.txt  # Count lines
```

### Step 2: Upload to HDFS

```bash
# Create input directory in HDFS
hdfs dfs -mkdir -p /user/hadoop/input

# Upload corpus to HDFS
hdfs dfs -put corpus.txt /user/hadoop/input/

# Verify upload
hdfs dfs -ls /user/hadoop/input/
hdfs dfs -du -h /user/hadoop/input/

# View sample data
hdfs dfs -head /user/hadoop/input/corpus.txt
```

### Step 3: Upload MapReduce Scripts

```bash
# On your local machine, copy scripts to master node
scp -i vockey.pem mapper.py reducer.py hadoop@<MASTER-PUBLIC-DNS>:~/

# On master node, make scripts executable
chmod +x mapper.py reducer.py

# Test scripts locally (optional)
echo "hello world hello" | python3 mapper.py | sort | python3 reducer.py
```

---

## MapReduce Job Execution

### Basic Word Count Job

```bash
# Create output directory (will be created by job, but clean if exists)
hdfs dfs -rm -r /user/hadoop/output/wordcount

# Run MapReduce job using Hadoop Streaming
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /user/hadoop/input/corpus.txt \
  -output /user/hadoop/output/wordcount \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py

# Monitor job progress (look for Job ID in output)
# Example: job_1234567890123_0001
```

### Alternative: Specify More Options

```bash
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -D mapreduce.job.name="WordCount-Lab5" \
  -D mapreduce.map.memory.mb=1024 \
  -D mapreduce.reduce.memory.mb=1024 \
  -input /user/hadoop/input/corpus.txt \
  -output /user/hadoop/output/wordcount \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py
```

---

## Experimentation

### Experiment A: Scaling (Recommended)

**Objective**: Compare job execution time with different cluster sizes

#### Test 1: 2 Core Nodes
```bash
# Modify cluster to have 2 core nodes (via EMR console)
# Resize instance group: Core -> 2 instances

# Clean previous output
hdfs dfs -rm -r /user/hadoop/output/wordcount-2nodes

# Run job and time it
time hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /user/hadoop/input/corpus.txt \
  -output /user/hadoop/output/wordcount-2nodes \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py

# Record execution time
```

#### Test 2: 4 Core Nodes
```bash
# Modify cluster to have 4 core nodes
# Resize instance group: Core -> 4 instances

# Clean previous output
hdfs dfs -rm -r /user/hadoop/output/wordcount-4nodes

# Run job and time it
time hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /user/hadoop/input/corpus.txt \
  -output /user/hadoop/output/wordcount-4nodes \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py

# Record execution time
```

**Expected Observation**: More nodes should reduce execution time due to parallel processing.

### Experiment B: Input Size Variation

```bash
# Create small dataset (first 10000 lines)
hdfs dfs -cat /user/hadoop/input/corpus.txt | head -10000 > small_corpus.txt
hdfs dfs -put small_corpus.txt /user/hadoop/input/

# Run job on small dataset
time hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /user/hadoop/input/small_corpus.txt \
  -output /user/hadoop/output/wordcount-small \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py

# Compare with full dataset execution time
```

### Experiment C: Fault Tolerance (Advanced)

```bash
# Start a long-running job
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /user/hadoop/input/corpus.txt \
  -output /user/hadoop/output/wordcount-fault \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py

# While job is running:
# 1. Go to EMR console
# 2. Terminate one core node
# 3. Observe job continues and completes (task reassignment)
# 4. Check YARN UI for failed task attempts
```

---

## Output Validation

### Check Output Files

```bash
# List output directory
hdfs dfs -ls /user/hadoop/output/wordcount/

# View part files
hdfs dfs -cat /user/hadoop/output/wordcount/part-00000 | head -20

# Count unique words
hdfs dfs -cat /user/hadoop/output/wordcount/part-* | wc -l

# Find most frequent words
hdfs dfs -cat /user/hadoop/output/wordcount/part-* | sort -t$'\t' -k2 -nr | head -20
```

### Copy Results to Local

```bash
# On master node, copy from HDFS to local
hdfs dfs -get /user/hadoop/output/wordcount ./wordcount_results

# From your local machine, download results
scp -i vockey.pem -r hadoop@<MASTER-PUBLIC-DNS>:~/wordcount_results ./
```

### Optional: Save to S3 (Persistent Storage)

```bash
# Create S3 bucket (use AWS Console or CLI)
# Example bucket name: emr-lab5-results-<your-id>

# Copy results to S3
aws s3 cp /home/hadoop/wordcount_results s3://emr-lab5-results-<your-id>/ --recursive
```

---

## YARN ResourceManager UI

**Access Web Interface**:
1. Get Master Public DNS
2. Enable SSH tunneling:
   ```bash
   ssh -i vockey.pem -L 8088:localhost:8088 hadoop@<MASTER-PUBLIC-DNS>
   ```
3. Open browser: `http://localhost:8088`
4. View running/completed applications

---

## Troubleshooting

### Common Issues

#### Issue 1: Permission Denied for Scripts
```bash
# Solution: Make scripts executable
chmod +x mapper.py reducer.py
```

#### Issue 2: Output Directory Already Exists
```bash
# Solution: Remove output directory
hdfs dfs -rm -r /user/hadoop/output/wordcount
```

#### Issue 3: Cluster Creation Fails (S3 Bucket)
```bash
# Solution: Uncheck "Publish cluster-specific logs to Amazon S3"
```

#### Issue 4: Cannot Connect to Master Node
```bash
# Solution 1: Check security group allows SSH (port 22)
# Solution 2: Verify key pair permissions (chmod 400 vockey.pem)
# Solution 3: Wait until cluster status is "Waiting"
```

#### Issue 5: Python Script Errors
```bash
# Test locally first
cat sample.txt | python3 mapper.py | sort | python3 reducer.py

# Check Python version on cluster
python3 --version
```

---

## Performance Metrics

### Record These Metrics

| Metric | Value |
|--------|-------|
| Dataset size | X MB |
| Number of nodes (2 cores) | Execution time: X seconds |
| Number of nodes (4 cores) | Execution time: X seconds |
| Total words processed | X words |
| Unique words | X unique |
| Map tasks | X tasks |
| Reduce tasks | X tasks |

---

## Cleanup

```bash
# Remove HDFS data
hdfs dfs -rm -r /user/hadoop/input
hdfs dfs -rm -r /user/hadoop/output

# Terminate EMR cluster (AWS Console)
# IMPORTANT: Always terminate cluster to avoid charges

# From EMR console:
# 1. Select cluster
# 2. Click "Terminate"
# 3. Confirm termination
```

---

## References

- [Apache Hadoop Streaming](https://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html)
- [AWS EMR Documentation](https://docs.aws.amazon.com/emr/)
- [MapReduce Tutorial](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)

---

## Repository Structure

```
emr-mapreduce-lab5/
├── README.md           # This file
├── mapper.py           # Map function
├── reducer.py          # Reduce function
├── results/            # Output results (add after execution)
│   └── sample_output.txt
└── screenshots/        # Demo screenshots (optional)
    ├── cluster_config.png
    ├── job_execution.png
    └── output_validation.png
```

---

## Notes

- Session timeout: EMR cluster stops when Learner Lab session ends
- Save results to S3 for persistence
- Document execution times for experiments
- Take screenshots for demo/report

---

