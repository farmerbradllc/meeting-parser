# Wayne County Voting Records - Complete Public Database System

A comprehensive solution for parsing, storing, and publicly displaying Wayne County, Indiana local government voting records.

## 🎯 Project Overview

This system transforms PDF meeting minutes into a searchable, public database with a modern web interface. It provides transparency and easy access to local government voting records.

**Live Features:**
- 🔍 Full-text search across all votes
- 👥 Individual official voting histories
- 📊 Meeting summaries and statistics
- 🏷️ Topic-based categorization
- 📱 Mobile-responsive design
- 🔌 JSON API for data access

## 📦 Complete System Components

### 1. PDF Parser (`voting_parser.py`)
Extracts voting records from PDF meeting minutes:
- Identifies motions, movers, seconders, and results
- Captures meeting attendance
- Categorizes votes by topic
- Outputs to CSV, JSON, or formatted text

### 2. Database System
- **Schema** (`database_schema.sql`) - Complete SQLite database structure
- **Import Tool** (`database_import.py`) - Loads parsed data into database
- Tables for meetings, officials, votes, attendance, and topics
- Pre-built views for common queries

### 3. Web Interface (`web_app.py`)
Flask-based public website:
- Browse recent meetings
- Search all voting records
- View official participation statistics
- Explore votes by topic
- RESTful API endpoints

### 4. Download Utilities
- `auto_download.py` - Automatic PDF scraper
- `download_meetings.sh` - Bash script for bulk downloads
- `download_meetings.bat` - Windows batch script

## 🚀 Quick Start

### Installation

```bash
# 1. Install Python 3.7+
# Download from python.org

# 2. Install dependencies
pip install PyPDF2 Flask

# 3. Download all files from this package
```

### Basic Usage

```bash
# Download PDFs
python auto_download.py --year 2025

# Parse to JSON
python voting_parser.py wayne_county_minutes/*.pdf --format json --output votes.json

# Create database
python database_import.py votes.json --database wayne_votes.db --schema database_schema.sql --init

# Start web server
python web_app.py
```

Visit http://localhost:5000 to see your public voting records website!

## 📁 File Structure

```
wayne-county-voting/
├── voting_parser.py          # PDF parser
├── database_schema.sql       # Database structure
├── database_import.py        # Import tool
├── web_app.py               # Web application
├── auto_download.py         # PDF downloader
├── download_meetings.sh     # Bash download script
├── download_meetings.bat    # Windows download script
├── requirements_full.txt    # Python dependencies
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── meeting.html
│   ├── officials.html
│   ├── official.html
│   ├── search.html
│   ├── topics.html
│   └── topic.html
└── static/
    └── css/
        └── style.css        # Stylesheet

Documentation:
├── README.md               # This file
├── QUICKSTART.md          # Quick start guide
├── DATABASE_SETUP.md      # Complete setup guide
└── EXAMPLES.md            # Usage examples
```

## 📊 Database Schema

### Core Tables

**meetings** - Meeting information
- Date, type, PDF reference
- Links to votes and attendance

**officials** - Council members & commissioners
- Name, role, active status
- Participation statistics

**votes** - Individual votes
- Motion text, mover, seconder
- Result, category, context

**attendance** - Meeting participation
- Links officials to meetings
- Tracks role at each meeting

**topics** - Vote categorization
- Budget transfers, hiring, resolutions, etc.
- Many-to-many with votes

### Built-in Views

- `official_statistics` - Participation metrics per official
- `meeting_summary` - Quick meeting overview
- `recent_votes` - Latest voting activity
- `topic_frequency` - Most common topics

## 🌐 Web Interface Pages

### Public Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Recent meetings, statistics, search |
| Meeting Detail | `/meeting/[id]` | Full meeting record with all votes |
| Officials List | `/officials` | All officials with participation stats |
| Official Detail | `/official/[id]` | Individual voting history |
| Search | `/search?q=keyword` | Full-text search across all votes |
| Topics | `/topics` | Browse by category |
| Topic Detail | `/topic/[id]` | All votes in a category |

### API Endpoints

| Endpoint | Returns |
|----------|---------|
| `/api/meetings` | All meetings (JSON) |
| `/api/officials` | All officials with stats (JSON) |
| `/api/votes/[meeting_id]` | Votes from meeting (JSON) |

## 🔧 Common Tasks

### Update with New Meetings

```bash
# Download latest PDFs
python auto_download.py --year 2025

# Parse new meetings
python voting_parser.py wayne_county_minutes/workshop-12-*.pdf --format json --output new.json

# Import to database
python database_import.py new.json
```

### Search the Database

```bash
# Using SQL directly
sqlite3 wayne_votes.db "SELECT * FROM recent_votes WHERE motion_text LIKE '%salary%';"

# Or use the web interface search
```

### Export Data

```bash
# Export all votes to CSV
sqlite3 -header -csv wayne_votes.db "SELECT * FROM votes;" > all_votes.csv

# Or use the parser
python voting_parser.py *.pdf --format csv --output votes.csv
```

### Backup Database

```bash
# Simple copy
cp wayne_votes.db backup_$(date +%Y%m%d).db

# Or SQLite backup
sqlite3 wayne_votes.db ".backup backup.db"
```

## 🎨 Customization

### Change Website Colors

Edit `static/css/style.css`:
```css
:root {
    --primary-color: #2c5aa0;      /* Your color */
    --secondary-color: #4a7bc8;    /* Your color */
}
```

### Add New Topics

```sql
INSERT INTO topics (topic_name, topic_description) VALUES
    ('Infrastructure', 'Roads, bridges, and public works');
```

### Modify Parsing Patterns

Edit `voting_parser.py` VOTE_PATTERNS list to recognize different voting language.

## 🚢 Deployment Options

### 1. Local Server
```bash
python web_app.py
# Access: http://localhost:5000
```

### 2. Network Server
```bash
python web_app.py
# Access: http://[your-ip]:5000
```

### 3. PythonAnywhere (Free)
1. Upload files to PythonAnywhere
2. Configure as Flask app
3. Public URL: yourname.pythonanywhere.com

### 4. Production Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### 5. Docker
```bash
docker build -t wayne-voting .
docker run -p 5000:5000 wayne-voting
```

## 📈 Use Cases

### For Citizens
- Track how officials vote
- Search specific topics (budgets, hiring, etc.)
- Monitor government transparency
- Research before elections

### For Journalists
- Quickly find voting patterns
- Export data for analysis
- Track specific issues over time
- Generate reports

### For Researchers
- Analyze voting behavior
- Study government efficiency
- Access structured data via API
- Export to statistical tools

### For Officials
- Review past decisions
- Prepare for meetings
- Track constituent interests
- Demonstrate accountability

## 🔐 Security & Privacy

- All data is from public records
- No authentication required (public records)
- Input sanitization prevents SQL injection
- Rate limiting recommended for production
- HTTPS recommended for public deployment

## 🐛 Troubleshooting

### Parser Issues
**Problem:** No votes found
**Solution:** Check PDF contains text (not scanned images), verify voting language matches patterns

### Database Issues
**Problem:** Database locked
**Solution:** Close other programs accessing the database, ensure only one web_app instance

### Web Interface Issues
**Problem:** 404 errors
**Solution:** Check templates/ and static/ folders exist, verify file structure

### Import Issues
**Problem:** Date parsing fails
**Solution:** Check date format in PDFs matches expected patterns, modify parse_date() function

## 📚 Documentation

- **QUICKSTART.md** - 5-minute setup guide
- **DATABASE_SETUP.md** - Complete database setup
- **EXAMPLES.md** - Usage examples and analysis scripts
- **README.md** - This file (overview)

## 🛠️ Technical Details

### Technologies
- **Python 3.7+** - Core language
- **PyPDF2** - PDF text extraction
- **Flask** - Web framework
- **SQLite** - Database (no server required)
- **HTML/CSS** - Frontend

### Browser Support
- Chrome, Firefox, Safari, Edge
- Mobile responsive
- No JavaScript required (progressive enhancement)

### Performance
- Handles thousands of votes
- Sub-second search
- Minimal server resources
- Can run on Raspberry Pi

## 🎯 Future Enhancements

Potential additions:
- [ ] Data visualization (charts, graphs)
- [ ] Email notifications for new meetings
- [ ] Advanced filtering (date ranges, multiple topics)
- [ ] Export to PDF reports
- [ ] Vote comparison tool
- [ ] Mobile app
- [ ] Integration with other county systems

## 📄 License

This tool is provided for public record access and government transparency. All voting data comes from official Wayne County sources.

## 🙏 Credits

Created for Wayne County, Indiana residents to access their local government voting records more easily.

## 📞 Support

**For Wayne County Records:**
- Phone: (765) 973-9200
- Website: https://waynecounty.in.gov

**For Technical Issues:**
- Check troubleshooting section
- Review documentation
- Examine log files

## 🚀 Getting Started Now

1. Read **QUICKSTART.md** for fastest setup
2. Read **DATABASE_SETUP.md** for complete guide
3. Check **EXAMPLES.md** for usage patterns
4. Start with `demo_parser.py` to see it in action

## 📊 Example Statistics

From a typical database:
- 100+ meetings archived
- 1,500+ votes recorded
- 10-15 active officials
- 95%+ votes unanimous
- 10+ topic categories

## 🎉 Success Stories

This system can help:
- ✅ Increase government transparency
- ✅ Improve citizen engagement
- ✅ Simplify records access
- ✅ Enable data-driven reporting
- ✅ Support democratic oversight

---

**Ready to make your local government more transparent?**

Start with: `python demo_parser.py`

Then follow **QUICKSTART.md** for the full system!
