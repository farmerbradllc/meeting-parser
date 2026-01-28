# Wayne County Meeting Minutes Voting Record Parser

A Python tool to parse and analyze voting records from Wayne County, Indiana local government meeting minutes PDFs.

## Features

- **Automatic PDF parsing**: Extracts text from PDF meeting minutes
- **Vote detection**: Identifies motions, movers, seconders, and results
- **Attendance tracking**: Extracts council members and commissioners present
- **Multiple output formats**: Text, CSV, JSON, and formal report formats
- **Batch processing**: Process multiple meeting minutes at once
- **Context extraction**: Captures the background/context of each vote

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install PyPDF2 directly:
```bash
pip install PyPDF2
```

2. Make the script executable (Linux/Mac):
```bash
chmod +x voting_parser.py
```

## Usage

### Basic Usage

Parse a single PDF and generate an official report:
```bash
python voting_parser.py workshop12-17-25.pdf
```

### Parse Multiple PDFs

Process multiple meeting minutes at once:
```bash
python voting_parser.py meeting1.pdf meeting2.pdf meeting3.pdf
```

### Output Formats

#### Official Report (default)
Generates a detailed, formatted report:
```bash
python voting_parser.py workshop12-17-25.pdf --format official
```

#### CSV Format
Generates a spreadsheet-compatible CSV file:
```bash
python voting_parser.py workshop12-17-25.pdf --format csv --output voting_records.csv
```

#### JSON Format
Generates structured JSON data:
```bash
python voting_parser.py workshop12-17-25.pdf --format json --output voting_records.json
```

#### Text Summary
Generates a simple text summary:
```bash
python voting_parser.py workshop12-17-25.pdf --format text
```

#### All Formats
Generate all report types at once:
```bash
python voting_parser.py workshop12-17-25.pdf --format all --output voting_analysis
```

This creates:
- `voting_analysis_summary.txt`
- `voting_analysis.csv`
- `voting_analysis.json`
- `voting_analysis_official.txt`

### Advanced Examples

#### Process all 2025 meetings
```bash
python voting_parser.py workshop*.pdf --format csv --output 2025_votes.csv
```

#### Generate JSON for data analysis
```bash
python voting_parser.py *.pdf --format json --output all_meetings.json
```

## Understanding the Output

### Official Report Format

```
WAYNE COUNTY COUNCIL & COMMISSIONERS
VOTING RECORD ANALYSIS REPORT
================================================================================

Report Generated: January 28, 2026 at 02:30 PM
Total Meetings Analyzed: 1
Total Votes Recorded: 15

================================================================================

MEETING: December 17, 2025
Source: workshop12-17-25.pdf
--------------------------------------------------------------------------------

ATTENDANCE:
  Council Members:
    • Beth Leisure
    • Max Smith
    • Gary Saunders
    ...

VOTING RECORD (15 items):

1. approve the November 19, 2025 workshop minutes
   Moved by: Beth Leisure
   Seconded by: Gary Saunders
   Result: all in favor
   Background: President Max Smith opened the meeting...

...
```

### CSV Format

| meeting_date | pdf_file | vote_number | motion | mover | seconder | result | context |
|--------------|----------|-------------|--------|-------|----------|--------|---------|
| December 17, 2025 | workshop12-17-25.pdf | 1 | approve the November 19... | Beth Leisure | Gary Saunders | all in favor | President Max Smith... |

### JSON Format

```json
[
  {
    "date": "December 17, 2025",
    "pdf_path": "workshop12-17-25.pdf",
    "attendees": ["Beth Leisure", "Max Smith", "Gary Saunders"],
    "commissioners": ["Brad Dwenger", "Jeff Plasterer", "Aaron Roberts"],
    "votes": [
      {
        "motion": "approve the November 19, 2025 workshop minutes",
        "mover": "Beth Leisure",
        "seconder": "Gary Saunders",
        "result": "all in favor",
        "context": "President Max Smith opened the meeting...",
        "line_number": 24
      }
    ]
  }
]
```

## What the Tool Captures

For each meeting, the parser extracts:

1. **Meeting Metadata**
   - Date of meeting
   - Council members present
   - Commissioners present
   - PDF source file

2. **For Each Vote**
   - Motion description (what was voted on)
   - Who made the motion (mover)
   - Who seconded the motion
   - Vote result (e.g., "all in favor", "5-2", etc.)
   - Context/background from surrounding text
   - Line number in the source document

## Downloading PDFs from Wayne County

To use this tool with Wayne County meeting minutes:

1. Visit the archive page: https://waynecounty.in.gov/minutes/archive/cw/councommwrkshp_arc.php
2. Click on any meeting date to download the PDF
3. Save the PDFs to a folder
4. Run the parser on your downloaded PDFs

Example workflow:
```bash
# Create a directory for your PDFs
mkdir wayne_county_minutes
cd wayne_county_minutes

# Download PDFs (manually or using wget/curl)
wget https://www.co.wayne.in.us/minutes/archive/cw/2025/workshop12-17-25.pdf
wget https://www.co.wayne.in.us/minutes/archive/cw/2025/workshop11-19-25.pdf

# Parse all PDFs in the directory
python ../voting_parser.py *.pdf --format all --output 2025_voting_analysis
```

## Voting Patterns Detected

The parser recognizes several common voting patterns:

1. `[Name] moved for approval, [Name] seconded with all in favor`
2. `[Name] moved to approve [motion], [Name] seconded with all in favor`
3. `[Name] moved for approval of [motion], [Name] seconded with [vote count]`

The tool is designed to handle Wayne County's specific formatting style.

## Customization

### Adding New Vote Patterns

If you encounter vote formats not currently recognized, you can add new patterns to the `VOTE_PATTERNS` list in the `VotingRecordParser` class:

```python
VOTE_PATTERNS = [
    # Your new pattern here
    r'new_pattern_regex',
    # Existing patterns...
]
```

### Modifying Output

The `ReportGenerator` class contains methods for each output format. You can customize these to match your specific needs.

## Troubleshooting

### No votes detected
- Verify the PDF contains actual text (not just images)
- Check if the voting language matches the patterns in the parser
- Try opening the PDF to ensure it's not corrupted

### Missing attendance information
- The parser looks for "Present:" and "Commissioner:" sections
- Ensure these sections appear near the beginning of the document

### Date not recognized
- The parser supports formats like "December 17, 2025" and "12/17/2025"
- If your PDFs use a different format, you may need to add a new date pattern

## Data Analysis Examples

Once you have the data in CSV or JSON format, you can analyze it:

### Count votes by council member (CSV)
```python
import pandas as pd

df = pd.read_csv('voting_records.csv')
print(df['mover'].value_counts())
```

### Find all votes on a specific topic (JSON)
```python
import json

with open('voting_records.json') as f:
    data = json.load(f)

for meeting in data:
    for vote in meeting['votes']:
        if 'transfer' in vote['motion'].lower():
            print(f"{meeting['date']}: {vote['motion']}")
```

## Contributing

To add support for other meeting types or improve parsing:

1. Add new regex patterns to `VOTE_PATTERNS`
2. Extend the `Vote` or `Meeting` dataclasses with new fields
3. Update the report generators to include new information

## Limitations

- Only works with text-based PDFs (not scanned images without OCR)
- Designed specifically for Wayne County's format
- May not capture unanimous consent items or voice votes without explicit "moved/seconded" language
- Date recognition is limited to specific formats

## License

This tool is provided as-is for public use in analyzing local government records.

## Support

For issues specific to Wayne County meeting minutes, contact:
- Wayne County Government: (765) 973-9200
- Website: https://waynecounty.in.gov

For tool-related questions, check the voting patterns and ensure your PDFs match the expected format.
