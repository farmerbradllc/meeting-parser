#!/usr/bin/env python3
"""
Database Import Tool for Wayne County Voting Records
Imports parsed voting records into SQLite database
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys


class VotingDatabase:
    """Database manager for Wayne County voting records"""
    
    def __init__(self, db_path="wayne_county_votes.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✓ Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def initialize_schema(self, schema_file="database_schema.sql"):
        """Create database tables from schema file"""
        try:
            with open(schema_file, 'r') as f:
                schema = f.read()
            
            # Execute schema
            self.cursor.executescript(schema)
            self.conn.commit()
            print("✓ Database schema initialized")
        except FileNotFoundError:
            print(f"✗ Schema file not found: {schema_file}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error initializing schema: {e}")
            sys.exit(1)
    
    def get_or_create_official(self, full_name: str, role: str = "Council Member") -> int:
        """Get official_id or create new official record"""
        # Check if official exists
        self.cursor.execute(
            "SELECT official_id FROM officials WHERE full_name = ?",
            (full_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Parse name
        parts = full_name.strip().split()
        first_name = parts[0] if parts else ""
        last_name = parts[-1] if len(parts) > 1 else ""
        
        # Create new official
        self.cursor.execute(
            """INSERT INTO officials (full_name, first_name, last_name, role)
               VALUES (?, ?, ?, ?)""",
            (full_name, first_name, last_name, role)
        )
        return self.cursor.lastrowid
    
    def parse_date(self, date_string: str) -> Optional[str]:
        """Parse date string to SQL format (YYYY-MM-DD)"""
        if not date_string:
            return None
        
        # Try common formats
        formats = [
            '%B %d, %Y',  # December 17, 2025
            '%m/%d/%Y',   # 12/17/2025
            '%m-%d-%Y',   # 12-17-2025
            '%Y-%m-%d',   # 2025-12-17
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_string.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def categorize_motion(self, motion_text: str, context: str = "") -> str:
        """Categorize motion by keywords"""
        text = (motion_text + " " + context).lower()
        
        categories = {
            'Budget Transfer': ['transfer', 'from ', 'to '],
            'Hiring': ['post', 'hire', 'position', 'employee'],
            'Salary': ['salary', 'wage', 'compensation', 'pay'],
            'Resolution': ['resolution'],
            'Ordinance': ['ordinance'],
            'Appointment': ['appoint', 'reappoint', 'board'],
            'Contract': ['contract', 'agreement', 'vendor'],
            'Grant': ['grant'],
            'Policy': ['policy'],
            'Minutes': ['minutes', 'approve the'],
            'Claims': ['claims', 'payment', 'invoice'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def import_meeting(self, meeting_data: Dict) -> int:
        """Import a single meeting and return meeting_id"""
        # Parse date
        meeting_date = self.parse_date(meeting_data.get('date', ''))
        if not meeting_date:
            print(f"⚠ Warning: Could not parse date '{meeting_data.get('date', '')}'")
            return None
        
        # Insert or get meeting
        self.cursor.execute(
            """INSERT OR IGNORE INTO meetings (meeting_date, meeting_type, pdf_filename)
               VALUES (?, ?, ?)""",
            (meeting_date, 'Workshop', Path(meeting_data.get('pdf_path', '')).name)
        )
        
        self.cursor.execute(
            "SELECT meeting_id FROM meetings WHERE meeting_date = ? AND meeting_type = ?",
            (meeting_date, 'Workshop')
        )
        meeting_id = self.cursor.fetchone()[0]
        
        # Import attendees
        for attendee in meeting_data.get('attendees', []):
            official_id = self.get_or_create_official(attendee, 'Council Member')
            self.cursor.execute(
                """INSERT OR IGNORE INTO attendance (meeting_id, official_id, role_at_meeting)
                   VALUES (?, ?, ?)""",
                (meeting_id, official_id, 'Council Member')
            )
        
        # Import commissioners
        for commissioner in meeting_data.get('commissioners', []):
            official_id = self.get_or_create_official(commissioner, 'Commissioner')
            self.cursor.execute(
                """INSERT OR IGNORE INTO attendance (meeting_id, official_id, role_at_meeting)
                   VALUES (?, ?, ?)""",
                (meeting_id, official_id, 'Commissioner')
            )
        
        # Import votes
        for vote_num, vote in enumerate(meeting_data.get('votes', []), 1):
            self.import_vote(meeting_id, vote_num, vote)
        
        self.conn.commit()
        return meeting_id
    
    def import_vote(self, meeting_id: int, vote_number: int, vote_data: Dict):
        """Import a single vote"""
        # Get official IDs
        mover_id = None
        if vote_data.get('mover'):
            mover_id = self.get_or_create_official(vote_data['mover'])
        
        seconder_id = None
        if vote_data.get('seconder'):
            seconder_id = self.get_or_create_official(vote_data['seconder'])
        
        # Parse result
        result = vote_data.get('result', '')
        is_unanimous = 'all in favor' in result.lower()
        
        # Try to extract vote counts (e.g., "5-2")
        yes_count = None
        no_count = None
        vote_match = re.match(r'(\d+)\s*[-–]\s*(\d+)', result)
        if vote_match:
            yes_count = int(vote_match.group(1))
            no_count = int(vote_match.group(2))
        
        # Categorize motion
        motion_category = self.categorize_motion(
            vote_data.get('motion', ''),
            vote_data.get('context', '')
        )
        
        # Insert vote
        self.cursor.execute(
            """INSERT INTO votes (
                meeting_id, vote_number, motion_text, motion_category,
                mover_id, seconder_id, result, is_unanimous,
                yes_count, no_count, context_text, line_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                meeting_id, vote_number, vote_data.get('motion', ''),
                motion_category, mover_id, seconder_id, result,
                is_unanimous, yes_count, no_count,
                vote_data.get('context', ''), vote_data.get('line_number')
            )
        )
        
        vote_id = self.cursor.lastrowid
        
        # Link to topics
        self.link_vote_to_topics(vote_id, motion_category)
    
    def link_vote_to_topics(self, vote_id: int, motion_category: str):
        """Link vote to relevant topics"""
        # Get topic_id
        self.cursor.execute(
            "SELECT topic_id FROM topics WHERE topic_name = ?",
            (motion_category,)
        )
        result = self.cursor.fetchone()
        
        if result:
            topic_id = result[0]
            self.cursor.execute(
                """INSERT OR IGNORE INTO vote_topics (vote_id, topic_id)
                   VALUES (?, ?)""",
                (vote_id, topic_id)
            )
    
    def import_from_json(self, json_file: str):
        """Import all meetings from a JSON file"""
        print(f"\n{'='*60}")
        print(f"Importing from: {json_file}")
        print(f"{'='*60}\n")
        
        try:
            with open(json_file, 'r') as f:
                meetings = json.load(f)
        except FileNotFoundError:
            print(f"✗ JSON file not found: {json_file}")
            return
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
            return
        
        imported_count = 0
        vote_count = 0
        
        for meeting in meetings:
            meeting_id = self.import_meeting(meeting)
            if meeting_id:
                imported_count += 1
                vote_count += len(meeting.get('votes', []))
                print(f"✓ Imported: {meeting.get('date', 'Unknown')} "
                      f"({len(meeting.get('votes', []))} votes)")
        
        self.conn.commit()
        
        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  Meetings imported: {imported_count}")
        print(f"  Votes imported: {vote_count}")
        print(f"{'='*60}\n")
    
    def get_statistics(self):
        """Get database statistics"""
        stats = {}
        
        # Total meetings
        self.cursor.execute("SELECT COUNT(*) FROM meetings")
        stats['total_meetings'] = self.cursor.fetchone()[0]
        
        # Total votes
        self.cursor.execute("SELECT COUNT(*) FROM votes")
        stats['total_votes'] = self.cursor.fetchone()[0]
        
        # Total officials
        self.cursor.execute("SELECT COUNT(*) FROM officials WHERE is_active = 1")
        stats['active_officials'] = self.cursor.fetchone()[0]
        
        # Unanimous votes
        self.cursor.execute("SELECT COUNT(*) FROM votes WHERE is_unanimous = 1")
        stats['unanimous_votes'] = self.cursor.fetchone()[0]
        
        if stats['total_votes'] > 0:
            stats['unanimous_percentage'] = (
                stats['unanimous_votes'] / stats['total_votes'] * 100
            )
        else:
            stats['unanimous_percentage'] = 0
        
        return stats
    
    def print_statistics(self):
        """Print database statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        print(f"Total Meetings:     {stats['total_meetings']}")
        print(f"Total Votes:        {stats['total_votes']}")
        print(f"Active Officials:   {stats['active_officials']}")
        print(f"Unanimous Votes:    {stats['unanimous_votes']} "
              f"({stats['unanimous_percentage']:.1f}%)")
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import Wayne County voting records into database'
    )
    parser.add_argument(
        'json_file',
        help='JSON file containing parsed voting records'
    )
    parser.add_argument(
        '--database',
        default='wayne_county_votes.db',
        help='Database file path (default: wayne_county_votes.db)'
    )
    parser.add_argument(
        '--schema',
        default='database_schema.sql',
        help='Schema file path (default: database_schema.sql)'
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize database schema (run first time only)'
    )
    
    args = parser.parse_args()
    
    # Create database manager
    db = VotingDatabase(args.database)
    db.connect()
    
    # Initialize schema if requested
    if args.init:
        db.initialize_schema(args.schema)
    
    # Import data
    db.import_from_json(args.json_file)
    
    # Print statistics
    db.print_statistics()
    
    # Close connection
    db.close()


if __name__ == '__main__':
    main()
