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
-- Recreate SECTION with composite PK (term_id, crn)
CREATE TABLE IF NOT EXISTS section (
  term_id          INTEGER NOT NULL,
  crn              TEXT    NOT NULL,
  course_id        TEXT    NOT NULL,
  section          TEXT,
  instruction_mode TEXT    NOT NULL,
  professor        TEXT,
  status           TEXT    NOT NULL,
  PRIMARY KEY (term_id, crn),
  FOREIGN KEY (course_id) REFERENCES course(course_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (term_id)   REFERENCES term(term_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- migrate data, then swap tables...

-- Recreate MEETING to reference the composite key
CREATE TABLE IF NOT EXISTS meeting (
  meeting_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  term_id     INTEGER NOT NULL,
  crn         TEXT    NOT NULL,
  day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN -1 AND 7),
  start_min   INTEGER NOT NULL,
  end_min     INTEGER NOT NULL,
  room        TEXT    NOT NULL,
  FOREIGN KEY (term_id, crn) REFERENCES section(term_id, crn)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_meeting_unique
ON meeting(term_id, crn, day_of_week);

DROP VIEW IF EXISTS open_classes;

CREATE VIEW open_classes AS
SELECT
  t.term,
  s.crn,
  s.course_id,
  c.subject,
  c.number,
  c.units,
  c.prereq,
  c.coreq,
  s.section,
  s.professor,
  s.status,
  m.day_of_week,
  m.start_min,
  m.end_min,
  m.room
FROM section AS s
JOIN term    AS t ON t.term_id   = s.term_id
JOIN course  AS c ON c.course_id = s.course_id
JOIN meeting AS m ON m.term_id   = s.term_id  -- safer if CRNs can repeat across terms
                 AND m.crn       = s.crn;

-- DROP VIEW IF EXISTS open_classes;

-- CREATE VIEW open_classes AS
-- SELECT
--   t.term,
--   s.course_id,
--   s.crn,
--   s.section,
--   c.subject,
--   c.number,
--   c.units,
--   c.prereq,
--   c.coreq,
--   s.instruction_mode,
--   s.professor,
--   s.status,
--   m.day_of_week,
--   m.start_min,
--   m.end_min,
--   m.room
-- FROM section AS s
-- JOIN term    AS t ON t.term_id   = s.term_id         -- inner join (must exist)
-- JOIN course  AS c ON c.course_id = s.course_id       -- inner join (must exist)
-- LEFT JOIN meeting AS m
--   ON m.term_id = s.term_id AND m.crn = s.crn;        -- keep rows even with no meeting

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_section_term   ON section(term_id);
CREATE INDEX IF NOT EXISTS idx_section_course ON section(course_id);
CREATE INDEX IF NOT EXISTS idx_meeting_crn    ON meeting(crn);
CREATE INDEX IF NOT EXISTS idx_meeting_time   ON meeting(day_of_week, start_min);
