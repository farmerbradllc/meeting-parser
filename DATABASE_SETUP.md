# Wayne County Voting Records Database & Web Interface Setup Guide

This guide will walk you through setting up the complete public-facing voting records system.

## Overview

The system consists of three main components:
1. **Parser** - Extracts voting records from PDFs
2. **Database** - Stores voting records in SQLite
3. **Web Interface** - Public-facing website to browse and search records

## System Architecture

```
PDF Files → voting_parser.py → JSON → database_import.py → SQLite Database → web_app.py → Public Website
```

## Prerequisites

### Required Software
- Python 3.7 or higher
- pip (Python package installer)

### Required Python Packages
```bash
pip install PyPDF2 Flask
```

## Step-by-Step Setup

### Step 1: Download Meeting PDFs

Option A - Automatic Download:
```bash
python auto_download.py --year 2025
```

Option B - Manual Download:
- Visit: https://waynecounty.in.gov/minutes/archive/cw/councommwrkshp_arc.php
- Download PDFs to a folder
- Note the folder location

### Step 2: Parse PDFs to JSON

Parse all downloaded PDFs into a JSON file:
```bash
python voting_parser.py wayne_county_minutes/*.pdf --format json --output voting_data.json
```

This creates `voting_data.json` with all parsed voting records.

### Step 3: Initialize the Database

Create the database with the proper schema:
```bash
python database_import.py voting_data.json --database wayne_county_votes.db --schema database_schema.sql --init
```

This creates `wayne_county_votes.db` with all tables, indexes, and views.

### Step 4: Import Data

If you've already initialized the database and want to add more data:
```bash
python database_import.py new_voting_data.json --database wayne_county_votes.db
```

### Step 5: Start the Web Server

Launch the public web interface:
```bash
python web_app.py
```

The website will be available at: http://localhost:5000

## Complete Workflow Example

Here's a complete workflow from start to finish:

```bash
# 1. Create project directory
mkdir wayne_county_voting
cd wayne_county_voting

# 2. Download all required files (from the outputs you received)
# - voting_parser.py
# - database_schema.sql
# - database_import.py
# - web_app.py
# - templates/ folder
# - static/ folder
# - auto_download.py

# 3. Install dependencies
pip install PyPDF2 Flask

# 4. Download meeting PDFs
python auto_download.py --year 2024
python auto_download.py --year 2025

# 5. Parse all PDFs to JSON
python voting_parser.py wayne_county_minutes/*.pdf --format json --output all_votes.json

# 6. Create and populate database
python database_import.py all_votes.json --database wayne_votes.db --schema database_schema.sql --init

# 7. Start web server
python web_app.py
```

Visit http://localhost:5000 to see your public voting records website!

## Database Structure

### Main Tables

**meetings** - Meeting information
- meeting_id, meeting_date, meeting_type, pdf_filename

**officials** - Council members and commissioners
- official_id, full_name, role, is_active

**votes** - Individual votes on motions
- vote_id, meeting_id, motion_text, mover_id, seconder_id, result

**attendance** - Who attended which meetings
- attendance_id, meeting_id, official_id

**topics** - Vote categorization
- topic_id, topic_name, topic_description

### Key Views

**official_statistics** - Participation stats per official
**meeting_summary** - Summary of each meeting
**recent_votes** - Most recent votes with names
**topic_frequency** - Most common vote topics

## Web Interface Features

### Public Pages

1. **Home Page** (/)
   - Recent meetings
   - Overall statistics
   - Quick search

2. **Meeting Detail** (/meeting/[id])
   - Full meeting info
   - Attendance list
   - All votes from that meeting

3. **Officials List** (/officials)
   - All council members and commissioners
   - Participation statistics

4. **Official Detail** (/official/[id])
   - Individual official's voting history
   - Motions made and seconded

5. **Search** (/search?q=keyword)
   - Full-text search of all votes
   - Search by keyword, topic, or official

6. **Topics** (/topics)
   - Browse votes by category
   - Budget, Hiring, Resolutions, etc.

### API Endpoints

The system also provides JSON API endpoints:

- `/api/meetings` - All meetings
- `/api/officials` - All officials with stats
- `/api/votes/[meeting_id]` - Votes from a specific meeting

## Updating the Database

### Adding New Meetings

When new meetings are published:

```bash
# 1. Download new PDFs
python auto_download.py --year 2025

# 2. Parse new PDFs
python voting_parser.py wayne_county_minutes/workshop-[new-dates].pdf --format json --output new_votes.json

# 3. Import to database
python database_import.py new_votes.json --database wayne_votes.db
```

The web interface will automatically show the new data.

## Deployment Options

### Option 1: Local Network Server

Run on a computer accessible to your local network:
```bash
python web_app.py
# Access from other computers: http://[your-ip]:5000
```

### Option 2: Cloud Hosting (PythonAnywhere)

1. Sign up at PythonAnywhere.com (free tier available)
2. Upload all files
3. Configure as Flask web app
4. Your site will be at: yourname.pythonanywhere.com

### Option 3: Self-Hosted Server

1. Install on a Linux server (Ubuntu, Debian, etc.)
2. Use Gunicorn + Nginx for production
3. Set up as a systemd service for auto-start

Example production setup:
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Option 4: Docker Container

Create a Dockerfile:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_app.py"]
```

Build and run:
```bash
docker build -t wayne-voting .
docker run -p 5000:5000 wayne-voting
```

## Customization

### Changing Colors/Branding

Edit `static/css/style.css`:
```css
:root {
    --primary-color: #2c5aa0;  /* Main color */
    --secondary-color: #4a7bc8; /* Secondary color */
}
```

### Adding New Features

The Flask app (`web_app.py`) can be extended with:
- Export functionality (CSV, PDF reports)
- Email notifications for new meetings
- User accounts and commenting
- Data visualization (charts, graphs)

### Custom Topics

Edit the topics in `database_schema.sql` or add via SQL:
```sql
INSERT INTO topics (topic_name, topic_description) VALUES
    ('Your Topic', 'Description of the topic');
```

## Maintenance

### Database Backup

```bash
# Backup
sqlite3 wayne_votes.db ".backup wayne_votes_backup.db"

# Or just copy the file
cp wayne_votes.db wayne_votes_backup_$(date +%Y%m%d).db
```

### Database Optimization

Run periodically:
```bash
sqlite3 wayne_votes.db "VACUUM;"
sqlite3 wayne_votes.db "ANALYZE;"
```

### Check Database Statistics

```bash
python database_import.py --database wayne_votes.db --stats
```

## Troubleshooting

### Database Locked Error
- Close any other programs accessing the database
- Make sure only one web_app.py instance is running

### No Data Showing
1. Check database exists: `ls -l wayne_votes.db`
2. Check database has data: `sqlite3 wayne_votes.db "SELECT COUNT(*) FROM meetings;"`
3. Check web app is using correct database path

### Parsing Issues
- Ensure PDFs contain text (not just scanned images)
- Verify PDF downloads completed successfully
- Check voting_parser.py output for errors

### Web Interface Issues
- Ensure Flask is installed: `pip install Flask`
- Check templates/ folder exists and contains all HTML files
- Check static/css/ folder contains style.css
- View browser console for JavaScript errors

## Security Considerations

For public deployment:

1. **Use HTTPS** - Obtain SSL certificate (Let's Encrypt)
2. **Rate Limiting** - Prevent API abuse
3. **Input Validation** - Already handled in search queries
4. **Regular Updates** - Keep Flask and dependencies updated
5. **Backup Strategy** - Daily automated backups

## Support Resources

### Database Queries

View all officials:
```bash
sqlite3 wayne_votes.db "SELECT * FROM officials;"
```

View recent votes:
```bash
sqlite3 wayne_votes.db "SELECT * FROM recent_votes LIMIT 10;"
```

Export to CSV:
```bash
sqlite3 -header -csv wayne_votes.db "SELECT * FROM votes;" > votes.csv
```

### Log Files

Monitor the web app:
```bash
python web_app.py 2>&1 | tee app.log
```

## Next Steps

1. Set up automated daily updates
2. Add data visualization (charts/graphs)
3. Create printable reports
4. Add email notifications
5. Set up analytics (track popular searches)
6. Create mobile-friendly responsive design improvements

## License & Disclaimer

This is an unofficial tool for public record access. All data comes from official Wayne County government sources. This tool simply makes the data more accessible and searchable.

## Contact

For Wayne County official records:
- Phone: (765) 973-9200
- Website: https://waynecounty.in.gov

## Conclusion

You now have a complete system for:
- ✅ Parsing PDF meeting minutes
- ✅ Storing data in a searchable database
- ✅ Providing a public web interface
- ✅ Keeping records updated
- ✅ Making government more transparent

The system is designed to be maintainable, extensible, and easy to deploy publicly!
