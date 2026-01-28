# Quick Start Guide - Wayne County Voting Record Parser

## Installation (On Your Own Computer)

### Step 1: Install Python
If you don't have Python installed:
- **Windows/Mac**: Download from https://www.python.org/downloads/
- **Linux**: Usually pre-installed, or use `sudo apt install python3 python3-pip`

### Step 2: Install Dependencies
Open a terminal/command prompt and run:
```bash
pip install PyPDF2
```

### Step 3: Download the Tool
Save these files to a folder:
- `voting_parser.py` - Main parser tool
- `requirements.txt` - Dependencies list
- `demo_parser.py` - Demo/test script (optional)

## Quick Start Examples

### Example 1: Parse a Single Meeting
```bash
python voting_parser.py workshop12-17-25.pdf
```

Output:
```
WAYNE COUNTY COUNCIL & COMMISSIONERS
VOTING RECORD ANALYSIS REPORT
================================================================================
Report Generated: January 28, 2026 at 02:45 PM
Total Meetings Analyzed: 1
Total Votes Recorded: 15
...
```

### Example 2: Create a CSV Spreadsheet
```bash
python voting_parser.py workshop12-17-25.pdf --format csv --output december_votes.csv
```

Open `december_votes.csv` in Excel to see:
- All votes in spreadsheet format
- Easy sorting and filtering
- Import into other tools

### Example 3: Process All Meetings from 2025
```bash
# Download all 2025 PDFs to a folder first, then:
python voting_parser.py workshop*.pdf --format all --output 2025_analysis
```

This creates:
- `2025_analysis_summary.txt` - Quick summary
- `2025_analysis.csv` - Spreadsheet format
- `2025_analysis.json` - Data format
- `2025_analysis_official.txt` - Full report

## How to Get Wayne County PDFs

### Method 1: Manual Download
1. Go to: https://waynecounty.in.gov/minutes/archive/cw/councommwrkshp_arc.php
2. Click on any meeting date
3. Save the PDF to your computer
4. Run the parser on the downloaded file

### Method 2: Bulk Download (Advanced)
If you're comfortable with command line:

```bash
# Create a folder
mkdir wayne_county_minutes
cd wayne_county_minutes

# Download specific files
wget https://www.co.wayne.in.us/minutes/archive/cw/2025/workshop12-17-25.pdf
wget https://www.co.wayne.in.us/minutes/archive/cw/2025/workshop11-19-25.pdf
# ... add more as needed

# Parse all at once
python ../voting_parser.py *.pdf --format csv --output all_meetings.csv
```

## Use Cases

### Track Council Member Activity
Generate a CSV and analyze who makes the most motions:
```bash
python voting_parser.py 2025/*.pdf --format csv --output 2025_votes.csv
```

Then open in Excel and use pivot tables or formulas.

### Research Specific Topics
Generate JSON format and search programmatically:
```bash
python voting_parser.py *.pdf --format json --output all_votes.json
```

Then use the JSON data to search for keywords, dates, or patterns.

### Generate Annual Reports
Process all meetings from a year:
```bash
python voting_parser.py 2024/*.pdf --format official --output 2024_annual_report.txt
```

## Troubleshooting

### "Module not found: PyPDF2"
```bash
pip install PyPDF2
```

### "Permission denied"
On Mac/Linux, make the script executable:
```bash
chmod +x voting_parser.py
```

### No votes found
- Make sure the PDF contains actual text (not just scanned images)
- Try opening the PDF manually to verify it's not corrupted
- Check if the voting language matches expected patterns

### Names not extracted correctly
The parser looks for the "Present:" section. If your PDF format is different, you may need to adjust the patterns.

## Understanding the Output

### What Gets Captured
For each vote, the parser finds:
- **Motion**: What was being voted on
- **Mover**: Who made the motion
- **Seconder**: Who seconded the motion
- **Result**: "all in favor", vote counts, etc.
- **Context**: Background information from the minutes

### Example Parsed Vote
```
Vote #1:
  Motion: approve the November 19, 2025 workshop minutes
  Moved by: Beth Leisure
  Seconded by: Gary Saunders
  Result: all in favor
  Background: President Max Smith opened the meeting...
```

## Advanced Usage

### Filter by Date Range
```bash
# Parse only specific months
python voting_parser.py workshop-10-*.pdf workshop-11-*.pdf workshop-12-*.pdf
```

### Custom Output Location
```bash
python voting_parser.py *.pdf --format csv --output ~/Documents/voting_analysis.csv
```

### Combine with Other Tools
Export to CSV and use with:
- Excel: Data analysis, pivot tables, charts
- Google Sheets: Collaborative analysis
- Python pandas: Advanced statistical analysis
- R: Statistical modeling

## Tips for Best Results

1. **Download PDFs locally** before parsing (faster than processing remote files)
2. **Process multiple meetings at once** for comparative analysis
3. **Use CSV format** for spreadsheet analysis
4. **Use JSON format** for programming/automation
5. **Use official format** for human-readable reports

## Getting Help

### Tool Issues
Check the README.md for detailed documentation.

### Wayne County Questions
- Phone: (765) 973-9200
- Website: https://waynecounty.in.gov

### Report a Bug
If the parser misses votes or has errors, check:
1. The PDF is valid and contains text
2. The voting language matches expected patterns
3. Consider submitting feedback or modifying the patterns

## Next Steps

1. Download some meeting PDFs from Wayne County
2. Run the demo: `python demo_parser.py`
3. Try parsing a real PDF: `python voting_parser.py yourfile.pdf`
4. Experiment with different output formats
5. Build your own analysis based on the data!
