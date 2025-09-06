import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Load the dataset
df = pd.read_csv('data/jobs_data.csv')

print("=== DATASET OVERVIEW ===")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print("\n=== DATA TYPES ===")
print(df.dtypes)
print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== FIRST FEW ROWS ===")
print(df.head(3))

print("\n=== DATE ANALYSIS ===")
print(f"Date range: {df['date_posted'].min()} to {df['date_posted'].max()}")
print("Jobs by date:")
print(df['date_posted'].value_counts().sort_index())

print("\n=== COMPANIES ===")
print(f"Unique companies: {df['company'].nunique()}")
print("Top 15 companies by job postings:")
print(df['company'].value_counts().head(15))

print("\n=== CATEGORIES ===")
print(f"Unique categories: {df['category'].nunique()}")
print("Job categories:")
print(df['category'].value_counts())

print("\n=== LOCATIONS ===")
print(f"Unique locations: {df['location'].nunique()}")
print("Top 20 locations:")
print(df['location'].value_counts().head(20))

print("\n=== KEYWORDS ANALYSIS ===")
print("Sample keywords:")
print(df['keywords'].head(10))

# Analyze keywords format and frequency
print("\n=== KEYWORD PATTERNS ===")
# Sample to understand keyword format
keywords_sample = df['keywords'].dropna().head(10).tolist()
for i, keywords in enumerate(keywords_sample):
    print(f"Sample {i+1}: {repr(keywords)}")

# Try to extract all unique keywords
print("\n=== EXTRACTING ALL KEYWORDS ===")
all_keywords = []
keyword_extraction_errors = 0

for idx, keywords_str in enumerate(df['keywords'].dropna()):
    try:
        # Keywords might be comma-separated or in other formats
        if ',' in str(keywords_str):
            keywords_list = [k.strip().lower() for k in str(keywords_str).split(',')]
        else:
            # Try to split by other delimiters or treat as single keyword
            keywords_list = [str(keywords_str).strip().lower()]
        
        all_keywords.extend([k for k in keywords_list if k and k != 'nan'])
    except Exception as e:
        keyword_extraction_errors += 1
        if idx < 5:  # Show first few errors
            print(f"Error processing keywords at row {idx}: {e}")

print(f"Total keyword extraction errors: {keyword_extraction_errors}")
print(f"Total keywords extracted: {len(all_keywords)}")

if all_keywords:
    keyword_counter = Counter(all_keywords)
    print("\nTop 30 keywords:")
    for keyword, count in keyword_counter.most_common(30):
        print(f"  {keyword}: {count}")

print("\n=== JOB DESCRIPTION ANALYSIS ===")
if 'job_description' in df.columns:
    df['description_length'] = df['job_description'].str.len()
    print("Job description length statistics:")
    print(df['description_length'].describe())
    
    # Check for common patterns
    print("\nCommon patterns in job descriptions:")
    print(f"Descriptions mentioning 'remote': {df['job_description'].str.contains('remote', case=False, na=False).sum()}")
    print(f"Descriptions mentioning 'python': {df['job_description'].str.contains('python', case=False, na=False).sum()}")
    print(f"Descriptions mentioning 'javascript': {df['job_description'].str.contains('javascript', case=False, na=False).sum()}")
    print(f"Descriptions mentioning 'aws': {df['job_description'].str.contains('aws', case=False, na=False).sum()}")
    salary_pattern = r'\$[0-9,]+'
    print(f"Descriptions mentioning salary/compensation: {df['job_description'].str.contains(salary_pattern, case=False, na=False).sum()}")

print("\n=== DATA QUALITY CHECKS ===")
print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"Empty job descriptions: {df['job_description'].isnull().sum()}")
print(f"Empty keywords: {df['keywords'].isnull().sum()}")

# Check for URL patterns in post_link
print(f"Valid URLs in post_link: {df['post_link'].str.startswith('http', na=False).sum()}")

print("\n=== REMOTE WORK ANALYSIS ===")
# Analyze location patterns for remote work
remote_keywords = ['remote', 'anywhere', 'global', 'worldwide', 'work from home', 'wfh']
df['is_remote'] = df['location'].str.contains('|'.join(remote_keywords), case=False, na=False)
print(f"Jobs with remote indicators in location: {df['is_remote'].sum()}")
print(f"Percentage of remote jobs: {df['is_remote'].mean()*100:.1f}%")

print("\n=== SAMPLE DATA FOR INSPECTION ===")
print("\nSample job posting:")
sample_idx = 0
print(f"Company: {df.iloc[sample_idx]['company']}")
print(f"Category: {df.iloc[sample_idx]['category']}")
print(f"Location: {df.iloc[sample_idx]['location']}")
print(f"Date: {df.iloc[sample_idx]['date_posted']}")
print(f"Keywords: {df.iloc[sample_idx]['keywords']}")
print(f"Description preview: {str(df.iloc[sample_idx]['job_description'])[:500]}...")