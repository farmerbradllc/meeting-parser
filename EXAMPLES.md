# Usage Examples - Wayne County Voting Record Parser

This file contains practical examples for using the voting record parser in different scenarios.

## Table of Contents
1. [Basic Parsing](#basic-parsing)
2. [Batch Processing](#batch-processing)
3. [Data Analysis](#data-analysis)
4. [Automation](#automation)
5. [Advanced Queries](#advanced-queries)

---

## Basic Parsing

### Example 1: Parse One Meeting
```bash
# Download and parse a single meeting
python voting_parser.py workshop12-17-25.pdf

# Save output to a file
python voting_parser.py workshop12-17-25.pdf --format official --output december_report.txt
```

### Example 2: Quick CSV for Spreadsheet
```bash
# Generate CSV for Excel/Google Sheets
python voting_parser.py workshop12-17-25.pdf --format csv --output votes.csv

# Open in Excel and create pivot tables to analyze:
# - Who makes the most motions?
# - Who seconds the most?
# - What types of motions are most common?
```

### Example 3: JSON for Programming
```bash
# Generate JSON for further processing
python voting_parser.py workshop12-17-25.pdf --format json --output votes.json

# Use with Python, JavaScript, or any language that reads JSON
```

---

## Batch Processing

### Example 4: Process All 2025 Meetings
```bash
# First, download all 2025 PDFs
python auto_download.py --year 2025

# Then parse them all
python voting_parser.py wayne_county_minutes/workshop*-25.pdf --format all --output 2025_analysis
```

### Example 5: Compare Two Years
```bash
# Download both years
python auto_download.py --year 2024
python auto_download.py --year 2025

# Parse each year separately
python voting_parser.py wayne_county_minutes/*-24.pdf --format csv --output 2024_votes.csv
python voting_parser.py wayne_county_minutes/*-25.pdf --format csv --output 2025_votes.csv

# Now compare in Excel or with Python pandas
```

### Example 6: Quarterly Reports
```bash
# Q1 2025 (Jan-Mar)
python voting_parser.py workshop-1-*-25.pdf workshop-2-*-25.pdf workshop-3-*-25.pdf \
    --format official --output Q1_2025_report.txt

# Q2 2025 (Apr-Jun)
python voting_parser.py workshop-4-*-25.pdf workshop-5-*-25.pdf workshop-6-*-25.pdf \
    --format official --output Q2_2025_report.txt
```

---

## Data Analysis

### Example 7: Participation Analysis (Python)
```python
import pandas as pd

# Load CSV data
df = pd.read_csv('2025_votes.csv')

# Count motions by person
motions = df['mover'].value_counts()
print("Motions made by council member:")
print(motions)

# Count seconds by person
seconds = df['seconder'].value_counts()
print("\nSeconds by council member:")
print(seconds)

# Total participation
participation = motions.add(seconds, fill_value=0)
print("\nTotal participation:")
print(participation.sort_values(ascending=False))
```

### Example 8: Topic Analysis (Python)
```python
import pandas as pd
import json

# Load JSON data for more detail
with open('all_meetings.json') as f:
    meetings = json.load(f)

# Find all votes about transfers
transfer_votes = []
for meeting in meetings:
    for vote in meeting['votes']:
        if 'transfer' in vote['motion'].lower():
            transfer_votes.append({
                'date': meeting['date'],
                'motion': vote['motion'],
                'result': vote['result']
            })

print(f"Found {len(transfer_votes)} votes about transfers")

# Find votes about hiring/posting positions
hiring_votes = []
for meeting in meetings:
    for vote in meeting['votes']:
        if 'post' in vote['motion'].lower() or 'hire' in vote['motion'].lower():
            hiring_votes.append({
                'date': meeting['date'],
                'motion': vote['motion']
            })

print(f"Found {len(hiring_votes)} votes about hiring")
```

### Example 9: Voting Patterns (Python)
```python
import pandas as pd

df = pd.read_csv('votes.csv')

# Create mover-seconder pairs
df['pair'] = df['mover'] + ' → ' + df['seconder']

# Most common pairs
print("Most common mover→seconder pairs:")
print(df['pair'].value_counts().head(10))

# Check for unanimous votes
unanimous = df[df['result'].str.contains('all in favor', case=False)]
print(f"\nUnanimous votes: {len(unanimous)}/{len(df)} ({len(unanimous)/len(df)*100:.1f}%)")
```

---

## Automation

### Example 10: Monthly Report Script
```bash
#!/bin/bash
# monthly_report.sh - Generate report for current month

YEAR=$(date +%Y)
MONTH=$(date +%-m)

# Download latest PDF
python auto_download.py --year $YEAR

# Find this month's PDF
PDF=$(ls wayne_county_minutes/workshop-${MONTH}-*-${YEAR}.pdf 2>/dev/null | head -1)

if [ -f "$PDF" ]; then
    # Generate report
    python voting_parser.py "$PDF" --format all --output "monthly_report_${YEAR}_${MONTH}"
    echo "Report generated: monthly_report_${YEAR}_${MONTH}"
else
    echo "No meeting found for $MONTH/$YEAR"
fi
```

### Example 11: Continuous Monitoring
```python
#!/usr/bin/env python3
# monitor.py - Check for new meetings and auto-generate reports

import os
import time
from pathlib import Path
from datetime import datetime
import subprocess

def check_for_new_meetings():
    """Check if new meeting PDFs are available"""
    # Download latest PDFs
    subprocess.run(['python', 'auto_download.py', '--year', str(datetime.now().year)])
    
    # Find any unprocessed PDFs
    processed_file = Path('processed_meetings.txt')
    processed = set()
    if processed_file.exists():
        processed = set(processed_file.read_text().splitlines())
    
    pdf_dir = Path('wayne_county_minutes')
    all_pdfs = set(p.name for p in pdf_dir.glob('*.pdf'))
    
    new_pdfs = all_pdfs - processed
    
    if new_pdfs:
        print(f"Found {len(new_pdfs)} new meetings!")
        for pdf in new_pdfs:
            print(f"  - {pdf}")
            # Process new PDF
            subprocess.run([
                'python', 'voting_parser.py',
                str(pdf_dir / pdf),
                '--format', 'all',
                '--output', f"report_{pdf.replace('.pdf', '')}"
            ])
            # Mark as processed
            processed.add(pdf)
        
        # Update processed list
        processed_file.write_text('\n'.join(sorted(processed)))
        print("Reports generated!")
    else:
        print("No new meetings found")

if __name__ == '__main__':
    # Run daily
    while True:
        print(f"\n[{datetime.now()}] Checking for new meetings...")
        check_for_new_meetings()
        # Check once per day
        time.sleep(86400)
```

---

## Advanced Queries

### Example 12: Search for Specific Topics
```python
import json

def search_votes(json_file, keyword):
    """Search all votes for a keyword"""
    with open(json_file) as f:
        meetings = json.load(f)
    
    results = []
    for meeting in meetings:
        for vote in meeting['votes']:
            if keyword.lower() in vote['motion'].lower() or \
               keyword.lower() in vote.get('context', '').lower():
                results.append({
                    'date': meeting['date'],
                    'motion': vote['motion'],
                    'mover': vote['mover'],
                    'result': vote['result']
                })
    
    return results

# Usage examples:
results = search_votes('all_meetings.json', 'salary')
print(f"Found {len(results)} votes about salary")

results = search_votes('all_meetings.json', 'sheriff')
print(f"Found {len(results)} votes related to sheriff")

results = search_votes('all_meetings.json', 'resolution')
print(f"Found {len(results)} votes on resolutions")
```

### Example 13: Extract Financial Transfers
```python
import re
import json

def extract_transfers(json_file):
    """Extract all financial transfer amounts"""
    with open(json_file) as f:
        meetings = json.load(f)
    
    transfers = []
    # Pattern to find dollar amounts: $X,XXX.XX or $XXX.XX
    amount_pattern = r'\$[\d,]+\.?\d*'
    
    for meeting in meetings:
        for vote in meeting['votes']:
            if 'transfer' in vote['motion'].lower():
                amounts = re.findall(amount_pattern, vote['context'])
                if amounts:
                    transfers.append({
                        'date': meeting['date'],
                        'amounts': amounts,
                        'context': vote['context'][:200]
                    })
    
    return transfers

# Find all transfers
transfers = extract_transfers('all_meetings.json')
print(f"Found {len(transfers)} transfer votes")

# Calculate total (would need more sophisticated parsing)
for t in transfers[:5]:
    print(f"{t['date']}: {', '.join(t['amounts'])}")
```

### Example 14: Attendance Tracking
```python
import json
from collections import Counter

def analyze_attendance(json_file):
    """Analyze attendance patterns"""
    with open(json_file) as f:
        meetings = json.load(f)
    
    # Count attendance
    council_attendance = Counter()
    commissioner_attendance = Counter()
    
    total_meetings = len(meetings)
    
    for meeting in meetings:
        for member in meeting['attendees']:
            council_attendance[member] += 1
        for commissioner in meeting['commissioners']:
            commissioner_attendance[commissioner] += 1
    
    print(f"Council Attendance (out of {total_meetings} meetings):")
    for member, count in council_attendance.most_common():
        pct = (count/total_meetings)*100
        print(f"  {member}: {count} ({pct:.1f}%)")
    
    print(f"\nCommissioner Attendance:")
    for commissioner, count in commissioner_attendance.most_common():
        pct = (count/total_meetings)*100
        print(f"  {commissioner}: {count} ({pct:.1f}%)")

analyze_attendance('all_meetings.json')
```

---

## Tips for Success

1. **Start Simple**: Parse one PDF first to verify everything works
2. **Use CSV for Excel**: Best for quick analysis and sharing
3. **Use JSON for Programming**: Best for custom analysis scripts
4. **Automate Downloads**: Use auto_download.py instead of manual downloads
5. **Process in Batches**: Parse multiple meetings at once for efficiency
6. **Save All Formats**: Use `--format all` to have options later

## Common Workflows

### Workflow 1: Monthly Analysis
1. Run auto_download.py at month end
2. Parse new meetings to CSV
3. Import to Excel
4. Create pivot tables and charts
5. Share with stakeholders

### Workflow 2: Annual Report
1. Download full year of PDFs
2. Parse to JSON
3. Run Python analysis scripts
4. Generate summary statistics
5. Export to official report format

### Workflow 3: Real-time Monitoring
1. Set up cron job to run auto_download.py daily
2. Automatically parse new meetings
3. Send email alerts for specific topics
4. Update dashboard with latest data

## Need Help?

- Check README.md for full documentation
- Run with `--help` flag for command options
- Test with demo_parser.py before using real PDFs
- Verify PDFs contain text (not just scanned images)
