#!/usr/bin/env python3
"""
Wayne County Voting Records - Public Web Interface
Flask web application to display voting records from the database
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['DATABASE'] = 'wayne_county_votes.db'


def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


@app.route('/')
def index():
    """Home page with recent meetings"""
    db = get_db()
    
    # Get recent meetings
    meetings = db.execute("""
        SELECT * FROM meeting_summary
        ORDER BY meeting_date DESC
        LIMIT 10
    """).fetchall()
    
    # Get statistics
    stats = db.execute("""
        SELECT 
            (SELECT COUNT(*) FROM meetings) as total_meetings,
            (SELECT COUNT(*) FROM votes) as total_votes,
            (SELECT COUNT(*) FROM officials WHERE is_active = 1) as active_officials,
            (SELECT COUNT(*) FROM votes WHERE is_unanimous = 1) as unanimous_votes
    """).fetchone()
    
    db.close()
    
    return render_template('index.html', meetings=meetings, stats=stats)


@app.route('/meeting/<int:meeting_id>')
def meeting_detail(meeting_id):
    """Detail page for a specific meeting"""
    db = get_db()
    
    # Get meeting info
    meeting = db.execute("""
        SELECT m.*, 
               (SELECT COUNT(*) FROM attendance WHERE meeting_id = m.meeting_id) as attendee_count,
               (SELECT COUNT(*) FROM votes WHERE meeting_id = m.meeting_id) as vote_count
        FROM meetings m
        WHERE m.meeting_id = ?
    """, (meeting_id,)).fetchone()
    
    if not meeting:
        db.close()
        return "Meeting not found", 404
    
    # Get attendees
    attendees = db.execute("""
        SELECT o.full_name, o.role, a.role_at_meeting
        FROM attendance a
        JOIN officials o ON a.official_id = o.official_id
        WHERE a.meeting_id = ?
        ORDER BY o.role, o.full_name
    """, (meeting_id,)).fetchall()
    
    # Get votes
    votes = db.execute("""
        SELECT v.*, 
               o1.full_name as mover_name,
               o2.full_name as seconder_name
        FROM votes v
        LEFT JOIN officials o1 ON v.mover_id = o1.official_id
        LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
        WHERE v.meeting_id = ?
        ORDER BY v.vote_number
    """, (meeting_id,)).fetchall()
    
    db.close()
    
    return render_template('meeting.html', meeting=meeting, attendees=attendees, votes=votes)


@app.route('/officials')
def officials_list():
    """List all officials with their statistics"""
    db = get_db()
    
    officials = db.execute("""
        SELECT * FROM official_statistics
        ORDER BY role, full_name
    """).fetchall()
    
    db.close()
    
    return render_template('officials.html', officials=officials)


@app.route('/official/<int:official_id>')
def official_detail(official_id):
    """Detail page for a specific official"""
    db = get_db()
    
    # Get official info
    official = db.execute("""
        SELECT * FROM officials WHERE official_id = ?
    """, (official_id,)).fetchone()
    
    if not official:
        db.close()
        return "Official not found", 404
    
    # Get statistics
    stats = db.execute("""
        SELECT 
            COUNT(DISTINCT a.meeting_id) as meetings_attended,
            COUNT(DISTINCT v1.vote_id) as motions_made,
            COUNT(DISTINCT v2.vote_id) as motions_seconded
        FROM officials o
        LEFT JOIN attendance a ON o.official_id = a.official_id
        LEFT JOIN votes v1 ON o.official_id = v1.mover_id
        LEFT JOIN votes v2 ON o.official_id = v2.seconder_id
        WHERE o.official_id = ?
    """, (official_id,)).fetchone()
    
    # Get recent motions made
    motions_made = db.execute("""
        SELECT v.*, m.meeting_date, o2.full_name as seconder_name
        FROM votes v
        JOIN meetings m ON v.meeting_id = m.meeting_id
        LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
        WHERE v.mover_id = ?
        ORDER BY m.meeting_date DESC
        LIMIT 20
    """, (official_id,)).fetchall()
    
    # Get recent seconds
    motions_seconded = db.execute("""
        SELECT v.*, m.meeting_date, o1.full_name as mover_name
        FROM votes v
        JOIN meetings m ON v.meeting_id = m.meeting_id
        LEFT JOIN officials o1 ON v.mover_id = o1.official_id
        WHERE v.seconder_id = ?
        ORDER BY m.meeting_date DESC
        LIMIT 20
    """, (official_id,)).fetchall()
    
    db.close()
    
    return render_template('official.html', 
                         official=official, 
                         stats=stats,
                         motions_made=motions_made,
                         motions_seconded=motions_seconded)


@app.route('/search')
def search():
    """Search votes by keyword"""
    query = request.args.get('q', '')
    
    if not query:
        return render_template('search.html', query='', results=[])
    
    db = get_db()
    
    # Search in motion text and context
    results = db.execute("""
        SELECT v.*, m.meeting_date,
               o1.full_name as mover_name,
               o2.full_name as seconder_name
        FROM votes v
        JOIN meetings m ON v.meeting_id = m.meeting_id
        LEFT JOIN officials o1 ON v.mover_id = o1.official_id
        LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
        WHERE v.motion_text LIKE ? OR v.context_text LIKE ?
        ORDER BY m.meeting_date DESC
        LIMIT 100
    """, (f'%{query}%', f'%{query}%')).fetchall()
    
    db.close()
    
    return render_template('search.html', query=query, results=results)


@app.route('/topics')
def topics_list():
    """List all topics with vote counts"""
    db = get_db()
    
    topics = db.execute("""
        SELECT * FROM topic_frequency
        ORDER BY vote_count DESC
    """).fetchall()
    
    db.close()
    
    return render_template('topics.html', topics=topics)


@app.route('/topic/<int:topic_id>')
def topic_detail(topic_id):
    """Detail page for a specific topic"""
    db = get_db()
    
    # Get topic info
    topic = db.execute("""
        SELECT * FROM topics WHERE topic_id = ?
    """, (topic_id,)).fetchone()
    
    if not topic:
        db.close()
        return "Topic not found", 404
    
    # Get all votes for this topic
    votes = db.execute("""
        SELECT v.*, m.meeting_date,
               o1.full_name as mover_name,
               o2.full_name as seconder_name
        FROM votes v
        JOIN vote_topics vt ON v.vote_id = vt.vote_id
        JOIN meetings m ON v.meeting_id = m.meeting_id
        LEFT JOIN officials o1 ON v.mover_id = o1.official_id
        LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
        WHERE vt.topic_id = ?
        ORDER BY m.meeting_date DESC
    """, (topic_id,)).fetchall()
    
    db.close()
    
    return render_template('topic.html', topic=topic, votes=votes)


@app.route('/api/meetings')
def api_meetings():
    """API endpoint for meetings data"""
    db = get_db()
    
    meetings = db.execute("""
        SELECT * FROM meeting_summary
        ORDER BY meeting_date DESC
    """).fetchall()
    
    db.close()
    
    return jsonify([dict(m) for m in meetings])


@app.route('/api/officials')
def api_officials():
    """API endpoint for officials data"""
    db = get_db()
    
    officials = db.execute("""
        SELECT * FROM official_statistics
        ORDER BY total_participation DESC
    """).fetchall()
    
    db.close()
    
    return jsonify([dict(o) for o in officials])


@app.route('/api/votes/<int:meeting_id>')
def api_votes(meeting_id):
    """API endpoint for votes in a meeting"""
    db = get_db()
    
    votes = db.execute("""
        SELECT v.*, 
               o1.full_name as mover_name,
               o2.full_name as seconder_name
        FROM votes v
        LEFT JOIN officials o1 ON v.mover_id = o1.official_id
        LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
        WHERE v.meeting_id = ?
        ORDER BY v.vote_number
    """, (meeting_id,)).fetchall()
    
    db.close()
    
    return jsonify([dict(v) for v in votes])


if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(app.config['DATABASE']):
        print(f"Error: Database not found at {app.config['DATABASE']}")
        print("Please run database_import.py first to create and populate the database.")
        exit(1)
    
    print("=" * 60)
    print("Wayne County Voting Records - Web Interface")
    print("=" * 60)
    print(f"Database: {app.config['DATABASE']}")
    print("\nStarting web server...")
    print("Access at: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
