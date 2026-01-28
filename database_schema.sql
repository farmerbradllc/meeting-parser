-- Wayne County Voting Records Database Schema
-- SQLite database for storing and querying meeting minutes and votes

-- Table: meetings
-- Stores information about each council/commissioner meeting
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date DATE NOT NULL,
    meeting_type VARCHAR(50) DEFAULT 'Workshop',
    pdf_filename VARCHAR(255),
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_date, meeting_type)
);

-- Table: officials
-- Stores information about council members and commissioners
CREATE TABLE IF NOT EXISTS officials (
    official_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(50) NOT NULL, -- 'Council Member' or 'Commissioner'
    is_active BOOLEAN DEFAULT 1,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(full_name)
);

-- Table: attendance
-- Tracks which officials attended which meetings
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    official_id INTEGER NOT NULL,
    role_at_meeting VARCHAR(50), -- Role they held at this specific meeting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id),
    FOREIGN KEY (official_id) REFERENCES officials(official_id),
    UNIQUE(meeting_id, official_id)
);

-- Table: votes
-- Stores information about each vote/motion
CREATE TABLE IF NOT EXISTS votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    vote_number INTEGER, -- Order within the meeting (1, 2, 3...)
    motion_text TEXT NOT NULL,
    motion_category VARCHAR(100), -- 'Transfer', 'Hiring', 'Approval', etc.
    mover_id INTEGER,
    seconder_id INTEGER,
    result VARCHAR(50), -- 'all in favor', '5-2', etc.
    is_unanimous BOOLEAN,
    yes_count INTEGER,
    no_count INTEGER,
    abstain_count INTEGER,
    context_text TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id),
    FOREIGN KEY (mover_id) REFERENCES officials(official_id),
    FOREIGN KEY (seconder_id) REFERENCES officials(official_id)
);

-- Table: vote_details
-- Stores individual official votes (for non-unanimous votes)
CREATE TABLE IF NOT EXISTS vote_details (
    vote_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_id INTEGER NOT NULL,
    official_id INTEGER NOT NULL,
    vote_value VARCHAR(20), -- 'yes', 'no', 'abstain', 'absent'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (official_id) REFERENCES officials(official_id),
    UNIQUE(vote_id, official_id)
);

-- Table: topics
-- Categorizes votes by topic/subject matter
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name VARCHAR(100) NOT NULL UNIQUE,
    topic_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: vote_topics
-- Many-to-many relationship between votes and topics
CREATE TABLE IF NOT EXISTS vote_topics (
    vote_topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    UNIQUE(vote_id, topic_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS idx_officials_name ON officials(full_name);
CREATE INDEX IF NOT EXISTS idx_votes_meeting ON votes(meeting_id);
CREATE INDEX IF NOT EXISTS idx_votes_mover ON votes(mover_id);
CREATE INDEX IF NOT EXISTS idx_votes_seconder ON votes(seconder_id);
CREATE INDEX IF NOT EXISTS idx_attendance_meeting ON attendance(meeting_id);
CREATE INDEX IF NOT EXISTS idx_attendance_official ON attendance(official_id);
CREATE INDEX IF NOT EXISTS idx_vote_details_vote ON vote_details(vote_id);
CREATE INDEX IF NOT EXISTS idx_vote_details_official ON vote_details(official_id);

-- Views for common queries

-- View: official_statistics
-- Summary statistics for each official
CREATE VIEW IF NOT EXISTS official_statistics AS
SELECT 
    o.official_id,
    o.full_name,
    o.role,
    COUNT(DISTINCT a.meeting_id) as meetings_attended,
    COUNT(DISTINCT v1.vote_id) as motions_made,
    COUNT(DISTINCT v2.vote_id) as motions_seconded,
    (COUNT(DISTINCT v1.vote_id) + COUNT(DISTINCT v2.vote_id)) as total_participation
FROM officials o
LEFT JOIN attendance a ON o.official_id = a.official_id
LEFT JOIN votes v1 ON o.official_id = v1.mover_id
LEFT JOIN votes v2 ON o.official_id = v2.seconder_id
WHERE o.is_active = 1
GROUP BY o.official_id, o.full_name, o.role;

-- View: meeting_summary
-- Summary of each meeting
CREATE VIEW IF NOT EXISTS meeting_summary AS
SELECT 
    m.meeting_id,
    m.meeting_date,
    m.meeting_type,
    COUNT(DISTINCT a.official_id) as officials_present,
    COUNT(DISTINCT v.vote_id) as total_votes,
    SUM(CASE WHEN v.is_unanimous = 1 THEN 1 ELSE 0 END) as unanimous_votes
FROM meetings m
LEFT JOIN attendance a ON m.meeting_id = a.meeting_id
LEFT JOIN votes v ON m.meeting_id = v.meeting_id
GROUP BY m.meeting_id, m.meeting_date, m.meeting_type;

-- View: recent_votes
-- Most recent votes with official names
CREATE VIEW IF NOT EXISTS recent_votes AS
SELECT 
    v.vote_id,
    m.meeting_date,
    v.motion_text,
    v.motion_category,
    o1.full_name as mover,
    o2.full_name as seconder,
    v.result,
    v.is_unanimous
FROM votes v
JOIN meetings m ON v.meeting_id = m.meeting_id
LEFT JOIN officials o1 ON v.mover_id = o1.official_id
LEFT JOIN officials o2 ON v.seconder_id = o2.official_id
ORDER BY m.meeting_date DESC, v.vote_number;

-- View: topic_frequency
-- Most common topics
CREATE VIEW IF NOT EXISTS topic_frequency AS
SELECT 
    t.topic_name,
    COUNT(vt.vote_id) as vote_count,
    MIN(m.meeting_date) as first_occurrence,
    MAX(m.meeting_date) as last_occurrence
FROM topics t
JOIN vote_topics vt ON t.topic_id = vt.topic_id
JOIN votes v ON vt.vote_id = v.vote_id
JOIN meetings m ON v.meeting_id = m.meeting_id
GROUP BY t.topic_id, t.topic_name
ORDER BY vote_count DESC;

-- Insert common topics
INSERT OR IGNORE INTO topics (topic_name, topic_description) VALUES
    ('Budget Transfer', 'Financial transfers between budget line items'),
    ('Hiring', 'Posting positions and hiring decisions'),
    ('Resolution', 'Formal resolutions and ordinances'),
    ('Salary', 'Salary adjustments and ordinances'),
    ('Appointment', 'Appointments to boards and committees'),
    ('Contract', 'Contract approvals and amendments'),
    ('Grant', 'Grant applications and acceptances'),
    ('Policy', 'Policy changes and updates'),
    ('Minutes', 'Approval of meeting minutes'),
    ('Claims', 'Payment of claims and invoices');
