-- ======================================================
-- Cavendish University EMS - Seed Data
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
-- ======================================================

-- 1. Demo Users
INSERT INTO users (email, password, name, role) VALUES
    ('admin@cavendish.ac.ug', 'admin', 'System Admin', 'admin'),
    ('registry@cavendish.ac.ug', 'registry', 'Registry Officer', 'registry'),
    ('finance@cavendish.ac.ug', 'finance', 'Finance Officer', 'finance'),
    ('lecturer@cavendish.ac.ug', 'lecturer', 'Dr. Mukasa', 'lecturer'),
    ('student@cavendish.ac.ug', 'student', 'Jane Doe', 'student'),
    ('john@cavendish.ac.ug', 'student', 'John Smith', 'student')
ON CONFLICT (email) DO NOTHING;

-- 2. Student Profiles
SELECT u.id, 'STU001', 'Jane Doe', 'student@cavendish.ac.ug', '+256 700 000000', 'Science and Technology', 'BSc Computer Science', 2
FROM users u WHERE u.email = 'student@cavendish.ac.ug'
ON CONFLICT (student_id) DO NOTHING;

INSERT INTO students (user_id, student_id, name, email, phone, faculty, program, year_of_study)
SELECT u.id, 'STU002', 'John Smith', 'john@cavendish.ac.ug', '+256 700 111111', 'Business Administration', 'BBA', 1
FROM users u WHERE u.email = 'john@cavendish.ac.ug'
ON CONFLICT (student_id) DO NOTHING;

-- 3. Sample Courses
INSERT INTO courses (code, name, credits, faculty, semester) VALUES
    ('CS101', 'Introduction to Programming', 3, 'Science and Technology', 'Semester 1'),
    ('CS102', 'Data Structures & Algorithms', 4, 'Science and Technology', 'Semester 1'),
    ('CS201', 'Database Systems', 3, 'Science and Technology', 'Semester 2'),
    ('CS202', 'Web Development', 3, 'Science and Technology', 'Semester 2'),
    ('MTH101', 'Calculus I', 3, 'Science', 'Semester 1'),
    ('BBA101', 'Principles of Management', 3, 'Business Administration', 'Semester 1'),
    ('BBA102', 'Financial Accounting', 3, 'Business Administration', 'Semester 1')
ON CONFLICT (code) DO NOTHING;

-- 4. Sample Enrollments
INSERT INTO enrollments (student_id, course_id)
SELECT s.id, c.id FROM students s, courses c
WHERE s.student_id = 'STU001' AND c.code IN ('CS101', 'CS102', 'MTH101')
ON CONFLICT (student_id, course_id) DO NOTHING;

-- 5. Sample Fees
INSERT INTO fees (student_id, amount_due, amount_paid, due_date, semester, status)
SELECT s.id, 3500000, 2000000, '2026-05-30', 'Semester 2', 'pending'
FROM students s WHERE s.student_id = 'STU001';

-- 6. Sample Results
INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'A', 85, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU001' AND c.code = 'CS101';

INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'A+', 92, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU001' AND c.code = 'CS102';

INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'B+', 78, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU001' AND c.code = 'MTH101';
