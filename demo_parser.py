#!/usr/bin/env python3
"""
Demo script showing the voting parser in action with pre-extracted text
"""

# Sample text from the December 17, 2025 meeting
SAMPLE_TEXT = """Council and Commissioners Workshop
December 17, 2025


Present: Beth Leisure
Max Smith
Gary Saunders
Cathy Williams
Jeff Cappa
Barry Ritter

Commissioner: Brad Dwenger
Jeff Plasterer
Aaron Roberts

Also Present: Bobbi Elsrod, Recording Secretary
Steve Higinbotham, County Administrator
Mark Hoelscher, Auditor
Simona Hiltner, Chief Deputy Auditor


President Max Smith opened the meeting at 6:00 PM and led the pledge to the flag.

Beth Leisure moved to approve the November 19, 2025 workshop minutes, Gary Saunders 
seconded with all in favor.
Brad Dwenger moved to approve the same minutes, Aaron Roberts seconded with all in favor.

Gary Callahan requested to transfer $52.65 from 1000.22120.000.0013 Printed Office Supplies 
to 1000.33810.000.0013 Dues, Subscriptions, Fees and $249.74 from 1000.10914.000.0013 
Payroll to 1000.10202.000.0013 Chief Deputy. Beth Leisure moved for approval, Cathy Williams
seconded with all in favor.

Lonnie McClintock requested to transfer $464.11 from 1000.33200.000.0660 Contractual 
Professional and $302.89 from 1000.22110.000.0660 Office Supplies to 1000.33201.000.0660 
Postage for a total of $767.00. Barry Ritter moved for approval, Gary Saunders seconded with all 
in favor.

Mr. McQueen requested to transfer $5,000 from 1000.33040.000.0200 Pauper Attorney to 
1000.33170.000.0200 Criminal Appeals. Jeff Cappa moved for approval of the transfer, Cathy 
Williams seconded with all in favor.

Mr. McQueen requested to post a clerical position that is open in the probation department. The 
position is a full-time position and budgeted for 2026. Beth Leisure moved to post and hire for the 
open probation clerical position, Jeff Cappa seconded with all in favor.

Gordon Moore requested to transfer $1,200 from 1202.13480.000.0000 Part-time 1 to 
1202.10100.000.0000 Elected Official. Beth Leisure moved for approval, Gary Saunders
seconded with all in favor.

Sheriff Retter requested approval of the sheriff's commissary fund resolution 2025-06. This brings 
the resolution up to date with state statute and the current commissary expenses. Cathy Williams
moved for approval of commissary resolution 2025-06, Jeff Cappa seconded with all in favor.

Salary ordinance 2025-03 for 2026 is ready for approval. Gary Saunders moved for approval, Jeff 
Cappa seconded with all in favor.
"""

import re
from typing import List, Dict
from collections import defaultdict


class SimpleVoteParser:
    """Simplified parser for demonstration"""
    
    def parse_votes(self, text: str):
        """Extract votes from text"""
        # Pattern: "Name moved for/to X, Name seconded with all in favor"
        pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+moved\s+(?:for|to)\s+([^,]+),\s*([A-Z][a-z]+\s+[A-Z][a-z]+)\s+seconded\s+with\s+(all in favor|[\d]+\s*[-–]\s*[\d]+)'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        votes = []
        for match in matches:
            votes.append({
                'mover': match.group(1),
                'motion': match.group(2).strip(),
                'seconder': match.group(3),
                'result': match.group(4)
            })
        
        return votes
    
    def extract_attendees(self, text: str):
        """Extract council members and commissioners"""
        lines = text.split('\n')
        
        attendees = []
        commissioners = []
        
        in_present = False
        in_commissioner = False
        
        for line in lines[:30]:
            line = line.strip()
            
            if line.startswith('Present:'):
                in_present = True
                in_commissioner = False
                continue
            elif line.startswith('Commissioner:'):
                in_commissioner = True
                in_present = False
                continue
            elif line.startswith('Also Present:'):
                break
            
            name_match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', line)
            if name_match:
                name = name_match.group(1)
                if in_present:
                    attendees.append(name)
                elif in_commissioner:
                    commissioners.append(name)
        
        return attendees, commissioners
    
    def voting_record_by_member(self, votes: List[Dict]) -> Dict:
        """Generate statistics by member"""
        stats = defaultdict(lambda: {'motions': 0, 'seconds': 0})
        
        for vote in votes:
            mover = vote['mover']
            seconder = vote['seconder']
            
            stats[mover]['motions'] += 1
            stats[seconder]['seconds'] += 1
        
        return dict(stats)


def main():
    parser = SimpleVoteParser()
    
    print("=" * 80)
    print("WAYNE COUNTY VOTING RECORD PARSER - DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Extract attendees
    attendees, commissioners = parser.extract_attendees(SAMPLE_TEXT)
    
    print("MEETING ATTENDEES:")
    print("-" * 80)
    print("Council Members:")
    for member in attendees:
        print(f"  • {member}")
    print("\nCommissioners:")
    for comm in commissioners:
        print(f"  • {comm}")
    
    print("\n" + "=" * 80)
    print()
    
    # Extract votes
    votes = parser.parse_votes(SAMPLE_TEXT)
    
    print(f"VOTING RECORD: {len(votes)} votes recorded")
    print("-" * 80)
    print()
    
    for idx, vote in enumerate(votes, 1):
        print(f"Vote #{idx}:")
        print(f"  Motion: {vote['motion']}")
        print(f"  Moved by: {vote['mover']}")
        print(f"  Seconded by: {vote['seconder']}")
        print(f"  Result: {vote['result']}")
        print()
    
    print("=" * 80)
    print()
    
    # Statistics
    stats = parser.voting_record_by_member(votes)
    
    print("PARTICIPATION STATISTICS:")
    print("-" * 80)
    print(f"{'Member':<20} {'Motions Made':<15} {'Seconds':<15}")
    print("-" * 80)
    
    for member in sorted(stats.keys()):
        motions = stats[member]['motions']
        seconds = stats[member]['seconds']
        print(f"{member:<20} {motions:<15} {seconds:<15}")
    
    print()
    print("=" * 80)
    print()
    print("This demonstrates the key functionality of the voting parser.")
    print("The full version (voting_parser.py) includes:")
    print("  • PDF extraction capability")
    print("  • Multiple output formats (CSV, JSON, text)")
    print("  • Batch processing of multiple files")
    print("  • Enhanced context extraction")
    print("  • Date parsing and meeting metadata")
    print()
    print("To use with actual PDFs, install PyPDF2 and run:")
    print("  python voting_parser.py your_meeting_minutes.pdf")
    print()


if __name__ == '__main__':
    main()
