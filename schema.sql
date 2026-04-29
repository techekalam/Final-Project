-- ======================================================
-- Cavendish University EMS - Database Schema
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
-- ======================================================

-- 1. Users Table (Authentication & Roles)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'registry', 'finance', 'lecturer', 'student')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Students Table (Profile Details)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    faculty VARCHAR(100),
    program VARCHAR(100),
    year_of_study INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Courses Table (Course Catalog)
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    credits INTEGER NOT NULL DEFAULT 3,
    faculty VARCHAR(100),
    semester VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Enrollments Table (Student-Course Link)
CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    UNIQUE(student_id, course_id)
);

-- 5. Fees Table (Tuition Tracking)
CREATE TABLE IF NOT EXISTS fees (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    amount_due DECIMAL(10,2) NOT NULL DEFAULT 0,
    amount_paid DECIMAL(10,2) NOT NULL DEFAULT 0,
    due_date DATE,
    semester VARCHAR(20),
    payment_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Results Table (Grades & Transcripts)
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    grade VARCHAR(5),
    score DECIMAL(5,2),
    semester VARCHAR(20),
    academic_year VARCHAR(20),
    entered_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, course_id, semester)
);

-- ======================================================
-- SEED DATA - Demo accounts and sample data
-- ======================================================

-- Demo Users
INSERT INTO users (email, password, name, role) VALUES
    ('admin@cavendish.ac.ug', 'admin', 'System Admin', 'admin'),
    ('registry@cavendish.ac.ug', 'registry', 'Registry Officer', 'registry'),
    ('finance@cavendish.ac.ug', 'finance', 'Finance Officer', 'finance'),
    ('lecturer@cavendish.ac.ug', 'lecturer', 'Dr. Mukasa', 'lecturer'),
    ('student@cavendish.ac.ug', 'student', 'Jane Doe', 'student'),
    ('john@cavendish.ac.ug', 'student', 'John Smith', 'student')
ON CONFLICT (email) DO NOTHING;

-- Student Profiles
INSERT INTO students (user_id, student_id, name, email, phone, faculty, program, year_of_study)
SELECT u.id, 'STU005', 'Jane Doe', 'student@cavendish.ac.ug', '+256 700 000000', 'Science and Technology', 'BSc Computer Science', 2
FROM users u WHERE u.email = 'student@cavendish.ac.ug'
ON CONFLICT (student_id) DO NOTHING;

INSERT INTO students (user_id, student_id, name, email, phone, faculty, program, year_of_study)
SELECT u.id, 'STU006', 'John Smith', 'john@cavendish.ac.ug', '+256 700 111111', 'Business Administration', 'BBA', 1
FROM users u WHERE u.email = 'john@cavendish.ac.ug'
ON CONFLICT (student_id) DO NOTHING;

-- Sample Courses
INSERT INTO courses (code, name, credits, faculty, semester) VALUES
    ('CS101', 'Introduction to Programming', 3, 'Science and Technology', 'Semester 1'),
    ('CS102', 'Data Structures & Algorithms', 4, 'Science and Technology', 'Semester 1'),
    ('CS201', 'Database Systems', 3, 'Science and Technology', 'Semester 2'),
    ('CS202', 'Web Development', 3, 'Science and Technology', 'Semester 2'),
    ('MTH101', 'Calculus I', 3, 'Science', 'Semester 1'),
    ('BBA101', 'Principles of Management', 3, 'Business Administration', 'Semester 1'),
    ('BBA102', 'Financial Accounting', 3, 'Business Administration', 'Semester 1')
ON CONFLICT (code) DO NOTHING;

-- Sample Enrollments
INSERT INTO enrollments (student_id, course_id)
SELECT s.id, c.id FROM students s, courses c
WHERE s.student_id = 'STU005' AND c.code IN ('CS101', 'CS102', 'MTH101')
ON CONFLICT (student_id, course_id) DO NOTHING;

-- Sample Fees
INSERT INTO fees (student_id, amount_due, amount_paid, due_date, semester, status)
SELECT s.id, 3500.00, 2000.00, '2026-05-30', 'Semester 2', 'pending'
FROM students s WHERE s.student_id = 'STU005';

-- Sample Results
INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'A', 85, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU005' AND c.code = 'CS101';

INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'A+', 92, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU005' AND c.code = 'CS102';

INSERT INTO results (student_id, course_id, grade, score, semester, academic_year)
SELECT s.id, c.id, 'B+', 78, 'Semester 1', '2025/2026'
FROM students s, courses c WHERE s.student_id = 'STU005' AND c.code = 'MTH101';
