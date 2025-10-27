-- schema.sql
PRAGMA foreign_keys = ON;

-- TERMS TABLE
CREATE TABLE IF NOT EXISTS term (
  term_id INTEGER PRIMARY KEY AUTOINCREMENT,
  term    TEXT NOT NULL UNIQUE
);

-- COURSE TABLE
CREATE TABLE IF NOT EXISTS course (
  course_id   TEXT PRIMARY KEY,
  subject     TEXT NOT NULL,
  number      TEXT NOT NULL,
  description TEXT,
  units       INTEGER NOT NULL,
  prereq      TEXT,
  coreq       TEXT
);

-- SECTION TABLE
-- Note: using CRN as the primary key (INTEGER)
CREATE TABLE IF NOT EXISTS section (
  crn              TEXT PRIMARY KEY,
  course_id        TEXT    NOT NULL,
  term_id          INTEGER NOT NULL,
  section          TEXT,               -- e.g., 01-LEC
  instruction_mode TEXT    NOT NULL,   -- e.g., In Person / Online
  professor        TEXT,
  status           TEXT    NOT NULL,   -- e.g., OPEN / CLOSED
  FOREIGN KEY (course_id) REFERENCES course(course_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (term_id)   REFERENCES term(term_id)
    ON UPDATE CASCADE ON DELETE CASCADE -- <- CHANGE TO restricted if you dont want all rows to be deleted
);

-- MEETING TABLE
-- start_min / end_min are minutes from midnight (e.g., 8:30am -> 510)
CREATE TABLE IF NOT EXISTS meeting (
  meeting_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  term_id     INTEGER NOT NULL,
  crn         TEXT NOT NULL,        -- FK to section.crn
  day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN -1 AND 7),
  start_min   INTEGER NOT NULL,
  end_min     INTEGER NOT NULL,
  room        TEXT    NOT NULL,
  FOREIGN KEY (crn) REFERENCES section(crn)
   ON UPDATE CASCADE ON DELETE CASCADE
  FOREIGN KEY (term_id) REFERENCES term(term_id)
   ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_meeting_unique
ON meeting(term_id, crn, day_of_week);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_section_term   ON section(term_id);
CREATE INDEX IF NOT EXISTS idx_section_course ON section(course_id);
CREATE INDEX IF NOT EXISTS idx_meeting_crn    ON meeting(crn);
CREATE INDEX IF NOT EXISTS idx_meeting_time   ON meeting(day_of_week, start_min);
