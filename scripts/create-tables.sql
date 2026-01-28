-- Wayne County Voting Records Database Schema
-- PostgreSQL/Neon database for storing and querying meeting minutes and votes

-- Table: meetings
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id SERIAL PRIMARY KEY,
    meeting_date DATE NOT NULL,
    meeting_type VARCHAR(50) DEFAULT 'Workshop',
    pdf_filename VARCHAR(255),
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_date, meeting_type)
);

-- Table: officials
CREATE TABLE IF NOT EXISTS officials (
    official_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: attendance
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id SERIAL PRIMARY KEY,
    meeting_id INTEGER NOT NULL REFERENCES meetings(meeting_id),
    official_id INTEGER NOT NULL REFERENCES officials(official_id),
    role_at_meeting VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_id, official_id)
);

-- Table: votes
CREATE TABLE IF NOT EXISTS votes (
    vote_id SERIAL PRIMARY KEY,
    meeting_id INTEGER NOT NULL REFERENCES meetings(meeting_id),
    vote_number INTEGER,
    motion_text TEXT NOT NULL,
    motion_category VARCHAR(100),
    mover_id INTEGER REFERENCES officials(official_id),
    seconder_id INTEGER REFERENCES officials(official_id),
    result VARCHAR(50),
    is_unanimous BOOLEAN,
    yes_count INTEGER,
    no_count INTEGER,
    abstain_count INTEGER,
    context_text TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: vote_details
CREATE TABLE IF NOT EXISTS vote_details (
    vote_detail_id SERIAL PRIMARY KEY,
    vote_id INTEGER NOT NULL REFERENCES votes(vote_id),
    official_id INTEGER NOT NULL REFERENCES officials(official_id),
    vote_value VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vote_id, official_id)
);

-- Table: topics
CREATE TABLE IF NOT EXISTS topics (
    topic_id SERIAL PRIMARY KEY,
    topic_name VARCHAR(100) NOT NULL UNIQUE,
    topic_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: vote_topics
CREATE TABLE IF NOT EXISTS vote_topics (
    vote_topic_id SERIAL PRIMARY KEY,
    vote_id INTEGER NOT NULL REFERENCES votes(vote_id),
    topic_id INTEGER NOT NULL REFERENCES topics(topic_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

-- Insert common topics
INSERT INTO topics (topic_name, topic_description) VALUES
    ('Budget Transfer', 'Financial transfers between budget line items'),
    ('Hiring', 'Posting positions and hiring decisions'),
    ('Resolution', 'Formal resolutions and ordinances'),
    ('Salary', 'Salary adjustments and ordinances'),
    ('Appointment', 'Appointments to boards and committees'),
    ('Contract', 'Contract approvals and amendments'),
    ('Grant', 'Grant applications and acceptances'),
    ('Policy', 'Policy changes and updates'),
    ('Minutes', 'Approval of meeting minutes'),
    ('Claims', 'Payment of claims and invoices')
ON CONFLICT (topic_name) DO NOTHING;

-- Insert sample data for demonstration
INSERT INTO officials (full_name, first_name, last_name, role, is_active) VALUES
    ('John Smith', 'John', 'Smith', 'Council Member', true),
    ('Mary Johnson', 'Mary', 'Johnson', 'Council Member', true),
    ('Robert Williams', 'Robert', 'Williams', 'Commissioner', true),
    ('Patricia Brown', 'Patricia', 'Brown', 'Commissioner', true),
    ('Michael Davis', 'Michael', 'Davis', 'Council Member', true)
ON CONFLICT (full_name) DO NOTHING;

INSERT INTO meetings (meeting_date, meeting_type, pdf_filename) VALUES
    ('2024-01-15', 'Regular Session', 'january_2024_regular.pdf'),
    ('2024-01-22', 'Workshop', 'january_2024_workshop.pdf'),
    ('2024-02-12', 'Regular Session', 'february_2024_regular.pdf'),
    ('2024-02-26', 'Workshop', 'february_2024_workshop.pdf'),
    ('2024-03-11', 'Regular Session', 'march_2024_regular.pdf')
ON CONFLICT (meeting_date, meeting_type) DO NOTHING;

-- Insert sample attendance
INSERT INTO attendance (meeting_id, official_id, role_at_meeting)
SELECT m.meeting_id, o.official_id, o.role
FROM meetings m, officials o
ON CONFLICT (meeting_id, official_id) DO NOTHING;

-- Insert sample votes
INSERT INTO votes (meeting_id, vote_number, motion_text, motion_category, mover_id, seconder_id, result, is_unanimous, yes_count, no_count) VALUES
    (1, 1, 'Approval of meeting minutes from December 2023', 'Minutes', 1, 2, 'all in favor', true, 5, 0),
    (1, 2, 'Transfer $15,000 from General Fund to Road Maintenance', 'Budget Transfer', 2, 3, 'all in favor', true, 5, 0),
    (1, 3, 'Approval to post Highway Department position', 'Hiring', 3, 4, '4-1', false, 4, 1),
    (2, 1, 'Discussion of proposed salary ordinance', 'Salary', 1, 5, 'all in favor', true, 5, 0),
    (3, 1, 'Approval of January 2024 claims', 'Claims', 4, 1, 'all in favor', true, 5, 0),
    (3, 2, 'Resolution 2024-001: Emergency Services Grant', 'Grant', 2, 3, 'all in favor', true, 5, 0),
    (3, 3, 'Appointment to Planning Commission', 'Appointment', 5, 2, '3-2', false, 3, 2),
    (4, 1, 'Review of contractor proposals for courthouse repairs', 'Contract', 3, 4, 'all in favor', true, 5, 0),
    (5, 1, 'Approval of February 2024 claims', 'Claims', 1, 2, 'all in favor', true, 5, 0),
    (5, 2, 'Policy update: Remote work guidelines', 'Policy', 4, 5, '4-1', false, 4, 1)
ON CONFLICT DO NOTHING;
