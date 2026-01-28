#!/usr/bin/env python3
"""
Wayne County Meeting Minutes Voting Record Parser
Extracts voting records from meeting minutes PDFs and generates structured reports.
"""

import re
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import PyPDF2
from pathlib import Path
import json
import csv


@dataclass
class Vote:
    """Represents a single vote on a motion"""
    motion_description: str
    mover: Optional[str] = None
    seconder: Optional[str] = None
    result: str = "Unknown"
    vote_details: Dict[str, str] = field(default_factory=dict)  # name: vote (yes/no/abstain)
    line_number: Optional[int] = None
    context: str = ""


@dataclass
class Meeting:
    """Represents a meeting with its votes"""
    date: Optional[datetime] = None
    date_string: str = ""
    attendees: List[str] = field(default_factory=list)
    commissioners: List[str] = field(default_factory=list)
    votes: List[Vote] = field(default_factory=list)
    pdf_path: str = ""


class VotingRecordParser:
    """Parser for Wayne County meeting minutes"""
    
    # Common voting patterns
    VOTE_PATTERNS = [
        # Pattern: "X moved for approval, Y seconded with all in favor"
        r'(?P<mover>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+moved\s+(?:for|to)\s+(?P<motion>[^,\.]+),\s*(?P<seconder>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+seconded\s+with\s+(?P<result>all in favor|[\d]+\s*[-–]\s*[\d]+)',
        
        # Pattern: "X moved for approval of Y, Z seconded with all in favor"
        r'(?P<mover>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+moved\s+for\s+(?P<motion>[^,]+),\s*(?P<seconder>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+seconded\s+with\s+(?P<result>all in favor|[\d]+\s*[-–]\s*[\d]+)',
        
        # Pattern: "X moved to approve..., Y seconded"
        r'(?P<mover>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+moved\s+to\s+(?P<motion>[^,]+),\s*(?P<seconder>[A-Z][a-z]+\s+[A-Z][a-z]+)\s+seconded',
    ]
    
    # Date patterns
    DATE_PATTERNS = [
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
    ]
    
    def __init__(self):
        self.compiled_vote_patterns = [re.compile(p, re.IGNORECASE) for p in self.VOTE_PATTERNS]
        self.compiled_date_patterns = [re.compile(p) for p in self.DATE_PATTERNS]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}", file=sys.stderr)
            return ""
    
    def parse_date(self, text: str) -> Tuple[Optional[datetime], str]:
        """Extract meeting date from text"""
        for pattern in self.compiled_date_patterns:
            match = pattern.search(text)
            if match:
                date_string = match.group(0)
                try:
                    # Try to parse the date
                    for fmt in ['%B %d, %Y', '%m/%d/%Y', '%m-%d-%Y']:
                        try:
                            date_obj = datetime.strptime(date_string, fmt)
                            return date_obj, date_string
                        except ValueError:
                            continue
                    return None, date_string
                except:
                    return None, date_string
        return None, ""
    
    def extract_attendees(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract attendees and commissioners from the beginning of the document"""
        attendees = []
        commissioners = []
        
        lines = text.split('\n')[:50]  # Check first 50 lines
        
        in_present_section = False
        in_commissioner_section = False
        
        for line in lines:
            line = line.strip()
            
            if re.match(r'^Present:', line, re.IGNORECASE):
                in_present_section = True
                in_commissioner_section = False
                continue
            elif re.match(r'^Commissioner:', line, re.IGNORECASE):
                in_commissioner_section = True
                in_present_section = False
                continue
            elif re.match(r'^Also Present:', line, re.IGNORECASE):
                break
            
            # Extract names (looks for capitalized first and last names)
            name_match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', line)
            if name_match:
                name = name_match.group(1)
                if in_present_section:
                    attendees.append(name)
                elif in_commissioner_section:
                    commissioners.append(name)
        
        return attendees, commissioners
    
    def find_motion_context(self, lines: List[str], vote_line_idx: int, context_lines: int = 3) -> str:
        """Find the context/description of what the vote is about"""
        # Look backwards for context
        start_idx = max(0, vote_line_idx - context_lines)
        context_lines_text = lines[start_idx:vote_line_idx]
        context = ' '.join([l.strip() for l in context_lines_text if l.strip()])
        return context
    
    def parse_votes(self, text: str) -> List[Vote]:
        """Extract all votes from the meeting minutes"""
        votes = []
        lines = text.split('\n')
        
        for idx, line in enumerate(lines):
            # Try each voting pattern
            for pattern in self.compiled_vote_patterns:
                match = pattern.search(line)
                if match:
                    groups = match.groupdict()
                    
                    # Get context from previous lines
                    context = self.find_motion_context(lines, idx)
                    
                    vote = Vote(
                        motion_description=groups.get('motion', '').strip(),
                        mover=groups.get('mover', '').strip() if groups.get('mover') else None,
                        seconder=groups.get('seconder', '').strip() if groups.get('seconder') else None,
                        result=groups.get('result', 'Unknown').strip(),
                        line_number=idx + 1,
                        context=context
                    )
                    
                    # Check if result indicates vote counts
                    result_match = re.match(r'(\d+)\s*[-–]\s*(\d+)', vote.result)
                    if result_match:
                        vote.vote_details = {
                            'yes': result_match.group(1),
                            'no': result_match.group(2)
                        }
                    
                    votes.append(vote)
                    break  # Found a match, no need to try other patterns
        
        return votes
    
    def parse_meeting(self, pdf_path: str) -> Meeting:
        """Parse a complete meeting minutes PDF"""
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return Meeting(pdf_path=pdf_path)
        
        # Extract meeting metadata
        date_obj, date_string = self.parse_date(text)
        attendees, commissioners = self.extract_attendees(text)
        votes = self.parse_votes(text)
        
        meeting = Meeting(
            date=date_obj,
            date_string=date_string,
            attendees=attendees,
            commissioners=commissioners,
            votes=votes,
            pdf_path=pdf_path
        )
        
        return meeting
    
    def parse_multiple_meetings(self, pdf_paths: List[str]) -> List[Meeting]:
        """Parse multiple meeting minutes PDFs"""
        meetings = []
        for pdf_path in pdf_paths:
            print(f"Parsing {pdf_path}...", file=sys.stderr)
            meeting = self.parse_meeting(pdf_path)
            meetings.append(meeting)
        return meetings


class ReportGenerator:
    """Generate reports from parsed meeting data"""
    
    @staticmethod
    def generate_summary_report(meetings: List[Meeting]) -> str:
        """Generate a text summary report"""
        report = ["=" * 80]
        report.append("WAYNE COUNTY MEETING MINUTES - VOTING RECORD SUMMARY")
        report.append("=" * 80)
        report.append("")
        
        for meeting in meetings:
            report.append(f"Meeting Date: {meeting.date_string or 'Unknown'}")
            report.append(f"PDF: {Path(meeting.pdf_path).name}")
            report.append("-" * 80)
            
            if meeting.attendees:
                report.append(f"Council Members Present: {', '.join(meeting.attendees)}")
            
            if meeting.commissioners:
                report.append(f"Commissioners Present: {', '.join(meeting.commissioners)}")
            
            report.append(f"\nTotal Votes: {len(meeting.votes)}")
            report.append("")
            
            for idx, vote in enumerate(meeting.votes, 1):
                report.append(f"Vote #{idx}:")
                report.append(f"  Motion: {vote.motion_description}")
                if vote.mover:
                    report.append(f"  Moved by: {vote.mover}")
                if vote.seconder:
                    report.append(f"  Seconded by: {vote.seconder}")
                report.append(f"  Result: {vote.result}")
                if vote.context:
                    report.append(f"  Context: {vote.context[:200]}...")
                report.append("")
            
            report.append("=" * 80)
            report.append("")
        
        return "\n".join(report)
    
    @staticmethod
    def generate_csv_report(meetings: List[Meeting], output_file: str):
        """Generate a CSV report of all votes"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['meeting_date', 'pdf_file', 'vote_number', 'motion', 
                         'mover', 'seconder', 'result', 'context']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for meeting in meetings:
                for idx, vote in enumerate(meeting.votes, 1):
                    writer.writerow({
                        'meeting_date': meeting.date_string or 'Unknown',
                        'pdf_file': Path(meeting.pdf_path).name,
                        'vote_number': idx,
                        'motion': vote.motion_description,
                        'mover': vote.mover or '',
                        'seconder': vote.seconder or '',
                        'result': vote.result,
                        'context': vote.context[:500]  # Limit context length
                    })
    
    @staticmethod
    def generate_json_report(meetings: List[Meeting], output_file: str):
        """Generate a JSON report of all meetings and votes"""
        data = []
        
        for meeting in meetings:
            meeting_data = {
                'date': meeting.date_string or 'Unknown',
                'pdf_path': meeting.pdf_path,
                'attendees': meeting.attendees,
                'commissioners': meeting.commissioners,
                'votes': []
            }
            
            for vote in meeting.votes:
                vote_data = {
                    'motion': vote.motion_description,
                    'mover': vote.mover,
                    'seconder': vote.seconder,
                    'result': vote.result,
                    'context': vote.context,
                    'line_number': vote.line_number
                }
                meeting_data['votes'].append(vote_data)
            
            data.append(meeting_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def generate_official_report(meetings: List[Meeting]) -> str:
        """Generate a detailed official-style report"""
        report = []
        
        # Overall statistics
        total_meetings = len(meetings)
        total_votes = sum(len(m.votes) for m in meetings)
        
        report.append("WAYNE COUNTY COUNCIL & COMMISSIONERS")
        report.append("VOTING RECORD ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nReport Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"Total Meetings Analyzed: {total_meetings}")
        report.append(f"Total Votes Recorded: {total_votes}")
        report.append("\n" + "=" * 80 + "\n")
        
        # Individual meeting details
        for meeting in meetings:
            report.append(f"MEETING: {meeting.date_string or 'Date Unknown'}")
            report.append(f"Source: {Path(meeting.pdf_path).name}")
            report.append("-" * 80)
            
            # Attendance
            report.append("\nATTENDANCE:")
            if meeting.attendees:
                report.append("  Council Members:")
                for member in meeting.attendees:
                    report.append(f"    • {member}")
            
            if meeting.commissioners:
                report.append("  Commissioners:")
                for commissioner in meeting.commissioners:
                    report.append(f"    • {commissioner}")
            
            # Votes
            report.append(f"\nVOTING RECORD ({len(meeting.votes)} items):")
            report.append("")
            
            for idx, vote in enumerate(meeting.votes, 1):
                report.append(f"{idx}. {vote.motion_description}")
                report.append(f"   Moved by: {vote.mover or 'Unknown'}")
                report.append(f"   Seconded by: {vote.seconder or 'Unknown'}")
                report.append(f"   Result: {vote.result}")
                
                if vote.context:
                    report.append(f"   Background: {vote.context[:300]}...")
                
                report.append("")
            
            report.append("=" * 80 + "\n")
        
        return "\n".join(report)


def main():
    """Main entry point for the voting record parser"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Parse voting records from Wayne County meeting minutes PDFs'
    )
    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='One or more PDF files to parse'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'csv', 'json', 'official', 'all'],
        default='official',
        help='Output format (default: official)'
    )
    parser.add_argument(
        '--output',
        help='Output file (for csv/json formats). If not specified, prints to stdout.'
    )
    
    args = parser.parse_args()
    
    # Parse meetings
    voting_parser = VotingRecordParser()
    meetings = voting_parser.parse_multiple_meetings(args.pdf_files)
    
    # Generate reports
    report_gen = ReportGenerator()
    
    if args.format == 'text':
        report = report_gen.generate_summary_report(meetings)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
    
    elif args.format == 'csv':
        output_file = args.output or 'voting_records.csv'
        report_gen.generate_csv_report(meetings, output_file)
        print(f"CSV report saved to {output_file}")
    
    elif args.format == 'json':
        output_file = args.output or 'voting_records.json'
        report_gen.generate_json_report(meetings, output_file)
        print(f"JSON report saved to {output_file}")
    
    elif args.format == 'official':
        report = report_gen.generate_official_report(meetings)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
    
    elif args.format == 'all':
        # Generate all formats
        base_name = args.output or 'voting_records'
        
        # Text report
        report = report_gen.generate_summary_report(meetings)
        with open(f"{base_name}_summary.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # CSV report
        report_gen.generate_csv_report(meetings, f"{base_name}.csv")
        
        # JSON report
        report_gen.generate_json_report(meetings, f"{base_name}.json")
        
        # Official report
        report = report_gen.generate_official_report(meetings)
        with open(f"{base_name}_official.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"All reports generated with base name '{base_name}'")


if __name__ == '__main__':
    main()
