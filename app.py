import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = None

if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("INFO: Supabase client initialized.")
    except Exception as e:
        print(f"WARNING: Could not connect to Supabase: {e}")
        supabase = None
else:
    print("WARNING: SUPABASE_URL and SUPABASE_KEY not found. Using Mock mode only.")


# --- Helper: check if a table exists by trying a lightweight query ---
def table_exists(table_name):
    if not supabase:
        return False
    try:
        supabase.table(table_name).select('id', count='exact').limit(0).execute()
        return True
    except Exception:
        return False


# ===================================================================
# MOCK DATA (mutable so updates persist during session)
# ===================================================================
MOCK_USERS = {
    "admin@cavendish.ac.ug":    {"id": 1, "email": "admin@cavendish.ac.ug",    "name": "System Admin",     "role": "admin",    "password": "admin"},
    "registry@cavendish.ac.ug": {"id": 2, "email": "registry@cavendish.ac.ug", "name": "Registry Officer", "role": "registry", "password": "registry"},
    "finance@cavendish.ac.ug":  {"id": 3, "email": "finance@cavendish.ac.ug",  "name": "Finance Officer",  "role": "finance",  "password": "finance"},
    "lecturer@cavendish.ac.ug": {"id": 4, "email": "lecturer@cavendish.ac.ug", "name": "Dr. Mukasa",       "role": "lecturer", "password": "lecturer"},
    "student@cavendish.ac.ug":  {"id": 5, "email": "student@cavendish.ac.ug",  "name": "Jane Doe",         "role": "student",  "password": "student"},
}

# Student-specific profiles
MOCK_PROFILES = {
    5: {"student_id": "CU-2026-001", "name": "Jane Doe",   "faculty": "Computer Science", "email": "student@cavendish.ac.ug", "phone": "+256 700 000000", "program": "BSc Computer Science"},
}

# Universal user profiles (for non-student stakeholders)
MOCK_USER_PROFILES = {
    1: {"name": "System Admin",     "email": "admin@cavendish.ac.ug",    "phone": "+256 700 100000", "department": "Administration"},
    2: {"name": "Registry Officer", "email": "registry@cavendish.ac.ug", "phone": "+256 700 200000", "department": "Registry"},
    3: {"name": "Finance Officer",  "email": "finance@cavendish.ac.ug",  "phone": "+256 700 300000", "department": "Finance"},
    4: {"name": "Dr. Mukasa",       "email": "lecturer@cavendish.ac.ug", "phone": "+256 700 400000", "department": "Computer Science"},
}

MOCK_COURSES = [
    {"id": 1, "code": "CS101",  "name": "Intro to Programming",       "credits": 3, "faculty": "Computer Science"},
    {"id": 2, "code": "CS102",  "name": "Data Structures & Algorithms","credits": 4, "faculty": "Computer Science"},
    {"id": 3, "code": "CS201",  "name": "Database Systems",           "credits": 3, "faculty": "Computer Science"},
    {"id": 4, "code": "CS202",  "name": "Web Development",            "credits": 3, "faculty": "Computer Science"},
    {"id": 5, "code": "MTH101", "name": "Calculus I",                 "credits": 3, "faculty": "Science"},
    {"id": 6, "code": "BBA101", "name": "Principles of Management",   "credits": 3, "faculty": "Business Administration"},
]

MOCK_ENROLLMENTS = {5: [1, 2, 5]}  # user_id -> list of course_ids

MOCK_RESULTS = {} # Real-time storage for mock grades
MOCK_GRADES = []  # For the global grade list view


# --- Serve Templates ---
@app.route('/')
def index():
    return render_template('index.html')


# ===================================================================
# API ENDPOINTS
# ===================================================================

# ---- Authentication ----
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if email != 'admin@cavendish.ac.ug' and not email.endswith('@student.cavendish.ac.ug'):
        return jsonify({"error": "Access denied. Only @student.cavendish.ac.ug or the admin can login."}), 403

    # Try Supabase first
    if table_exists('users'):
        try:
            response = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
            if response.data and len(response.data) > 0:
                user = response.data[0]
                user.pop('password', None)
                return jsonify({"user": user}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            print(f"Supabase login error, falling back to mock: {e}")

    # Fallback to mock
    mock_user = MOCK_USERS.get(email)
    if mock_user and mock_user['password'] == password:
        safe = {k: v for k, v in mock_user.items() if k != 'password'}
        return jsonify({"user": safe}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# ---- Student Profile (GET & PUT) ----
@app.route('/api/student/profile', methods=['GET', 'PUT'])
def student_profile():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        user_id = int(user_id)

        if table_exists('students'):
            try:
                res = supabase.table('students').select('*').eq('user_id', user_id).execute()
                if res.data:
                    return jsonify({"profile": res.data[0]}), 200
            except Exception as e:
                print(f"Supabase profile GET error: {e}")

        # Mock fallback
        profile = MOCK_PROFILES.get(user_id, {"student_id": "CU-2026-001", "name": "Unknown", "faculty": "N/A", "email": "", "phone": "", "program": ""})
        return jsonify({"profile": profile}), 200

    if request.method == 'PUT':
        data = request.json
        user_id = data.get('user_id')
        profile_data = data.get('profile', {})

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        user_id = int(user_id)

        if table_exists('students'):
            try:
                res = supabase.table('students').update(profile_data).eq('user_id', user_id).execute()
                return jsonify({"message": "Profile updated successfully", "data": res.data}), 200
            except Exception as e:
                print(f"Supabase profile PUT error: {e}")

        # Mock: actually update the in-memory profile
        if user_id in MOCK_PROFILES:
            MOCK_PROFILES[user_id].update(profile_data)
        else:
            MOCK_PROFILES[user_id] = profile_data

        return jsonify({"message": "Profile updated successfully", "profile": MOCK_PROFILES.get(user_id)}), 200


# ---- Student Registration (Admin creates new student) ----
@app.route('/api/student/register', methods=['POST'])
def register_student():
    global MOCK_NEXT_ID
    data = request.json
    name    = data.get('name')
    email   = data.get('email')
    phone   = data.get('phone', '')
    faculty = data.get('faculty', '')
    program = data.get('program', '')

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    if not email.endswith('@student.cavendish.ac.ug'):
        return jsonify({"error": "Students must be registered with a @student.cavendish.ac.ug email."}), 400

    if table_exists('users') and table_exists('students'):
        try:
            user_res = supabase.table('users').insert({
                "email": email, "password": "student", "name": name, "role": "student"
            }).execute()

            if user_res.data:
                new_user_id = user_res.data[0]['id']
                # Generate consecutive STUXXX IDs
                count_res = supabase.table('students').select('id', count='exact').execute()
                count = count_res.count or 0
                student_id = f"STU{str(count + 1).zfill(3)}"
                
                supabase.table('students').insert({
                    "user_id": new_user_id, "student_id": student_id,
                    "name": name, "email": email, "phone": phone,
                    "faculty": faculty, "program": program
                }).execute()
                return jsonify({"message": f"Student registered successfully. ID: {student_id}"}), 201
        except Exception as e:
            print(f"Supabase register error: {e}")
            return jsonify({"error": str(e)}), 500

    # Mock registration
    MOCK_NEXT_ID += 1
    sid = f"STU{str(len(MOCK_PROFILES) + 1).zfill(3)}"
    MOCK_USERS[email] = {"id": MOCK_NEXT_ID, "email": email, "name": name, "role": "student", "password": "student"}
    MOCK_PROFILES[MOCK_NEXT_ID] = {"student_id": sid, "name": name, "email": email, "phone": phone, "faculty": faculty, "program": program}
    return jsonify({"message": f"Student registered successfully. ID: {sid}"}), 201


# ---- User Profile for all stakeholders (GET & PUT) ----
@app.route('/api/user/profile', methods=['GET', 'PUT'])
def user_profile():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        user_id = int(user_id)

        if table_exists('users'):
            try:
                res = supabase.table('users').select('id, name, email, role, profile_pic').eq('id', user_id).execute()
                if res.data:
                    return jsonify({"profile": res.data[0]}), 200
            except Exception as e:
                print(f"Supabase user profile GET error: {e}")

        # Mock fallback
        profile = MOCK_USER_PROFILES.get(user_id, {"name": "Unknown", "email": "", "phone": "", "department": ""})
        return jsonify({"profile": profile}), 200

    if request.method == 'PUT':
        data = request.json
        user_id = data.get('user_id')
        profile_data = data.get('profile', {})

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        user_id = int(user_id)

        if table_exists('users'):
            try:
                update_data = {}
                if 'name' in profile_data:
                    update_data['name'] = profile_data['name']
                if 'profile_pic' in profile_data:
                    update_data['profile_pic'] = profile_data['profile_pic']
                if update_data:
                    supabase.table('users').update(update_data).eq('id', user_id).execute()
                return jsonify({"message": "Profile updated successfully"}), 200
            except Exception as e:
                print(f"Supabase user profile PUT error: {e}")

        # Mock update
        if user_id in MOCK_USER_PROFILES:
            MOCK_USER_PROFILES[user_id].update(profile_data)
        else:
            MOCK_USER_PROFILES[user_id] = profile_data

        # Also update the MOCK_USERS name
        for email, u in MOCK_USERS.items():
            if u['id'] == user_id and 'name' in profile_data:
                u['name'] = profile_data['name']
                break

        return jsonify({"message": "Profile updated successfully", "profile": MOCK_USER_PROFILES.get(user_id)}), 200


# ---- Courses (GET & POST) ----
@app.route('/api/courses', methods=['GET', 'POST', 'DELETE'])
def manage_courses():
    global MOCK_NEXT_COURSE_ID, MOCK_COURSES

    if request.method == 'GET':
        if table_exists('courses'):
            try:
                res = supabase.table('courses').select('*').execute()
                return jsonify({"courses": res.data}), 200
            except Exception as e:
                print(f"Supabase courses error: {e}")
        return jsonify({"courses": MOCK_COURSES}), 200

    if request.method == 'POST':
        data = request.json
        code    = data.get('code', '').strip()
        name    = data.get('name', '').strip()
        credits = data.get('credits', 3)
        faculty = data.get('faculty', '').strip()

        if not code or not name:
            return jsonify({"error": "Course code and name are required"}), 400

        if table_exists('courses'):
            try:
                res = supabase.table('courses').insert({
                    "code": code, "name": name, "credits": credits, "faculty": faculty
                }).execute()
                return jsonify({"message": f"Course {code} created successfully"}), 201
            except Exception as e:
                print(f"Supabase course create error: {e}")
                return jsonify({"error": str(e)}), 500

        # Mock: check for duplicate code
        for c in MOCK_COURSES:
            if c['code'] == code:
                return jsonify({"error": f"Course code {code} already exists"}), 400

        MOCK_NEXT_COURSE_ID += 1
        new_course = {"id": MOCK_NEXT_COURSE_ID, "code": code, "name": name, "credits": int(credits), "faculty": faculty}
        MOCK_COURSES.append(new_course)
        return jsonify({"message": f"Course {code} created successfully"}), 201

    if request.method == 'DELETE':
        course_id = request.args.get('id')
        if not course_id:
            return jsonify({"error": "Course ID is required"}), 400
        
        if table_exists('courses'):
            try:
                supabase.table('courses').delete().eq('id', course_id).execute()
                return jsonify({"message": "Course deleted successfully"}), 200
            except Exception as e:
                print(f"Supabase course delete error: {e}")
                return jsonify({"error": str(e)}), 500
        
        # Mock delete
        MOCK_COURSES = [c for c in MOCK_COURSES if str(c['id']) != str(course_id)]
        return jsonify({"message": "Course deleted successfully"}), 200


# ---- Course Enrollment ----
@app.route('/api/student/enroll', methods=['POST'])
def enroll_course():
    data = request.json
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if table_exists('enrollments') and table_exists('students'):
        try:
            # Look up the actual student_id from the students table using the user_id
            stu = supabase.table('students').select('id').eq('user_id', student_id).execute()
            if not stu.data:
                return jsonify({"error": "Student profile not found. Please contact Admin."}), 404
            
            sid = stu.data[0]['id']
            res = supabase.table('enrollments').insert({"student_id": sid, "course_id": course_id}).execute()
            return jsonify({"message": "Successfully enrolled"}), 200
        except Exception as e:
            print(f"Supabase enroll error: {e}")
            return jsonify({"error": str(e)}), 500

    # Mock enrollment
    uid = int(student_id) if student_id else 5
    if uid not in MOCK_ENROLLMENTS:
        MOCK_ENROLLMENTS[uid] = []
    cid = int(course_id)
    if cid in MOCK_ENROLLMENTS[uid]:
        return jsonify({"error": "Already enrolled in this course"}), 400
    MOCK_ENROLLMENTS[uid].append(cid)
    return jsonify({"message": "Successfully enrolled"}), 200


# ---- Student Enrollments List ----
@app.route('/api/student/enrollments', methods=['GET'])
def get_student_enrollments():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"enrollments": []}), 200
    user_id = int(user_id)

    if table_exists('enrollments') and table_exists('students'):
        try:
            stu = supabase.table('students').select('id').eq('user_id', user_id).execute()
            if stu.data:
                sid = stu.data[0]['id']
                res = supabase.table('enrollments').select('course_id').eq('student_id', sid).execute()
                ids = [e['course_id'] for e in res.data] if res.data else []
                return jsonify({"enrollments": ids}), 200
        except Exception as e:
            print(f"Supabase enrollments error: {e}")

    return jsonify({"enrollments": MOCK_ENROLLMENTS.get(user_id, [])}), 200


# ---- Student Dashboard Data ----
@app.route('/api/student/dashboard', methods=['GET'])
def get_student_dashboard():
    user_id = request.args.get('user_id')

    if table_exists('results') and table_exists('fees') and table_exists('enrollments'):
        try:
            stu = supabase.table('students').select('id').eq('user_id', user_id).execute()
            if stu.data:
                sid = stu.data[0]['id']
                results = supabase.table('results').select('score').eq('student_id', sid).execute()
                scores = [r['score'] for r in results.data] if results.data else []

                fees = supabase.table('fees').select('amount_due, amount_paid').eq('student_id', sid).execute()
                balance = sum((f['amount_due'] - f['amount_paid']) for f in fees.data) if fees.data else 0

                enrolled = supabase.table('enrollments').select('courses(code, name)').eq('student_id', sid).execute()
                lessons = []
                if enrolled.data:
                    for i, e in enumerate(enrolled.data):
                        if e.get('courses'):
                            lessons.append({"date": f"2026-05-0{i+1}", "course": e['courses']['name'], "time": f"{9+i}:00 AM"})

                return jsonify({
                    "performance": scores,
                    "upcoming_lessons": lessons,
                    "fee_balance": float(balance),
                    "enrolled_count": len(lessons)
                }), 200
        except Exception as e:
            print(f"Supabase student dash error: {e}")

    uid = int(user_id) if user_id else 5
    enrolled_count = len(MOCK_ENROLLMENTS.get(uid, []))
    return jsonify({
        "performance": [85, 90, 78, 92, 88],
        "upcoming_lessons": [
            {"date": "2026-05-01", "course": "Intro to Programming", "time": "10:00 AM"},
            {"date": "2026-05-02", "course": "Data Structures", "time": "02:00 PM"},
            {"date": "2026-05-03", "course": "Calculus I", "time": "09:00 AM"}
        ],
        "fee_balance": 5500000.00,
        "enrolled_count": max(enrolled_count, 3)
    }), 200


# ---- Admin Dashboard Data ----
@app.route('/api/admin/dashboard', methods=['GET'])
def get_admin_dashboard():
    if table_exists('students') and table_exists('fees'):
        try:
            students_res = supabase.table('students').select('id', count='exact').execute()
            total_students = students_res.count or 0

            fees_res = supabase.table('fees').select('amount_paid').execute()
            revenue = sum(f['amount_paid'] for f in fees_res.data) if fees_res.data else 0

            pending = 0
            if table_exists('results'):
                pending_res = supabase.table('results').select('id', count='exact').is_('grade', 'null').execute()
                pending = pending_res.count or 0

            # Real Activity Feed
            recent_activity = []
            if table_exists('students'):
                stus = supabase.table('students').select('name, created_at').order('created_at', desc=True).limit(2).execute()
                for s in stus.data:
                    recent_activity.append({"action": "New Registration", "student": s['name'], "time": s['created_at'][:10]})
            
            if table_exists('results'):
                grades = supabase.table('results').select('*, students(name)').order('created_at', desc=True).limit(3).execute()
                for g in grades.data:
                    name = g.get('students', {}).get('name', 'Student')
                    recent_activity.append({"action": f"Grade Entered: {g['grade']}", "student": name, "time": g['created_at'][:10]})
            
            if not recent_activity:
                recent_activity = [{"action": "No activity", "student": "System", "time": "—"}]

            return jsonify({
                "total_revenue": float(revenue),
                "new_admissions": total_students,
                "pending_results": pending,
                "recent_activity": sorted(recent_activity, key=lambda x: x['time'], reverse=True)[:5]
            }), 200
        except Exception as e:
            print(f"Supabase admin dash error: {e}")

    student_count = sum(1 for u in MOCK_USERS.values() if u['role'] == 'student')
    return jsonify({
        "total_revenue": 125000000.00,
        "new_admissions": max(student_count, 45),
        "pending_results": 12,
        "recent_activity": [
            {"action": "Enrolled in CS101",   "student": "Jane Doe",   "time": "2 mins ago"},
            {"action": "Paid Tuition",        "student": "John Smith", "time": "1 hr ago"},
            {"action": "Updated Profile",     "student": "Alice W.",   "time": "3 hrs ago"},
            {"action": "New Registration",    "student": "David K.",   "time": "5 hrs ago"}
        ]
    }), 200

MOCK_FEES_DATA = [
    {"id": 1, "amount_due": 12500000.00, "amount_paid": 7000000.00, "due_date": "2026-05-30", "semester": "Semester 1", "status": "partial"},
    {"id": 2, "amount_due": 12500000.00, "amount_paid": 12500000.00, "due_date": "2025-11-30", "semester": "Semester 2 (2025)", "status": "paid"},
]

# ---- Fees / Tuition ----
@app.route('/api/fees', methods=['GET', 'POST', 'PUT'])
def manage_fees():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if table_exists('fees') and table_exists('students'):
            try:
                stu = supabase.table('students').select('id').eq('user_id', user_id).execute()
                if stu.data:
                    sid = stu.data[0]['id']
                    res = supabase.table('fees').select('*').eq('student_id', sid).execute()
                    return jsonify({"fees": res.data}), 200
            except Exception as e:
                print(f"Supabase fees error: {e}")

        return jsonify({"fees": MOCK_FEES_DATA}), 200

    if request.method == 'POST':
        data = request.json
        student_id_str = data.get('student_id')
        amount_due     = data.get('amount_due')
        semester       = data.get('semester', 'Semester 1')
        due_date       = data.get('due_date')

        if table_exists('fees') and table_exists('students'):
            try:
                stu = supabase.table('students').select('id').eq('student_id', student_id_str).execute()
                if not stu.data:
                    return jsonify({"error": "Student not found"}), 404
                sid = stu.data[0]['id']
                res = supabase.table('fees').insert({
                    "student_id": sid, "amount_due": float(amount_due),
                    "amount_paid": 0, "semester": semester, "due_date": due_date,
                    "status": "pending"
                }).execute()
                return jsonify({"message": "Fee record added successfully"}), 201
            except Exception as e:
                print(f"Supabase fees POST error: {e}")
                return jsonify({"error": str(e)}), 500
        
        return jsonify({"error": "Database not connected"}), 500

    if request.method == 'PUT':
        data = request.json
        fid = data.get('id')
        paid = data.get('amount_paid')

        if not fid or paid is None:
            return jsonify({"error": "Record ID and amount paid are required"}), 400

        if table_exists('fees'):
            try:
                # Fetch current record to get the amount_due
                curr = supabase.table('fees').select('amount_due').eq('id', int(fid)).execute()
                if not curr.data:
                    return jsonify({"error": "Fee record not found"}), 404
                
                due = float(curr.data[0]['amount_due'])
                p = float(paid)
                status = 'paid' if p >= due else ('partial' if p > 0 else 'pending')

                res = supabase.table('fees').update({
                    "amount_paid": p,
                    "status": status
                }).eq('id', int(fid)).execute()
                return jsonify({"message": "Fee record updated successfully"}), 200
            except Exception as e:
                print(f"Supabase fees PUT error: {e}")
                return jsonify({"error": str(e)}), 500
        
        # Mock Update Support
        for f in MOCK_FEES_DATA:
            if f['id'] == int(fid):
                f['amount_paid'] = float(paid)
                f['status'] = 'paid' if f['amount_paid'] >= f['amount_due'] else ('partial' if f['amount_paid'] > 0 else 'pending')
                return jsonify({"message": "Mock fee record updated"}), 200

        return jsonify({"error": "Record not found"}), 404


# ---- Results / Grades ----
@app.route('/api/results', methods=['GET', 'POST', 'PUT'])
def manage_results():
    if request.method == 'GET':
        user_id_str = request.args.get('user_id')
        if not user_id_str:
            return jsonify({"results": []}), 200
        user_id = int(user_id_str)

        if table_exists('results') and table_exists('students'):
            try:
                stu = supabase.table('students').select('id').eq('user_id', user_id).execute()
                if stu.data:
                    sid = stu.data[0]['id']
                    res = supabase.table('results').select('*, courses(code, name)').eq('student_id', sid).execute()
                    return jsonify({"results": res.data}), 200
            except Exception as e:
                print(f"Supabase results GET error: {e}")

        # Mock fallback - only show what has been manually entered
        res_list = MOCK_RESULTS.get(user_id, [])
        return jsonify({"results": res_list}), 200

    if request.method == 'PUT':
        data = request.json
        res_id = data.get('id')
        score = data.get('score')
        grade = data.get('grade')
        if table_exists('results'):
            try:
                supabase.table('results').update({"score": score, "grade": grade}).eq('id', res_id).execute()
                return jsonify({"message": "Result updated successfully"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return jsonify({"message": "Mock result updated"}), 200

    if request.method == 'POST':
        data = request.json
        if table_exists('results'):
            try:
                res = supabase.table('results').insert(data).execute()
                return jsonify({"message": "Result saved", "data": res.data}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return jsonify({"message": "Result saved (Mock)"}), 201


# ---- Lecturer: Grade Input ----
@app.route('/api/grades', methods=['GET', 'POST'])
def manage_grades():
    global MOCK_NEXT_GRADE_ID

    if request.method == 'GET':
        if table_exists('results'):
            try:
                res = supabase.table('results').select('*, courses(code, name), students(student_id, name)').execute()
                return jsonify({"grades": res.data}), 200
            except Exception as e:
                print(f"Supabase grades GET error: {e}")
        return jsonify({"grades": MOCK_GRADES}), 200

    if request.method == 'POST':
        data = request.json
        student_id_str = data.get('student_id', '')
        course_id      = data.get('course_id')
        score          = data.get('score')
        grade          = data.get('grade', '')
        semester       = data.get('semester', 'Semester 1')

        if not student_id_str or not course_id or score is None or not grade:
            return jsonify({"error": "Student, course, score, and grade are required"}), 400

        if table_exists('results') and table_exists('students'):
            try:
                stu = supabase.table('students').select('id').eq('student_id', student_id_str).execute()
                if not stu.data:
                    return jsonify({"error": "Student not found"}), 404
                sid = stu.data[0]['id']
                res = supabase.table('results').insert({
                    "student_id": sid, "course_id": int(course_id),
                    "score": float(score), "grade": grade, "semester": semester,
                    "academic_year": "2025/2026"
                }).execute()
                return jsonify({"message": "Grade submitted successfully"}), 201
            except Exception as e:
                print(f"Supabase grade POST error: {e}")
                return jsonify({"error": str(e)}), 500

        # Mock: find student name and course name
        student_name = student_id_str
        target_uid = None
        for uid, p in MOCK_PROFILES.items():
            if p.get('student_id') == student_id_str:
                student_name = p['name']
                target_uid = uid
                break
        
        course_code = ""
        course_name = ""
        for c in MOCK_COURSES:
            if str(c['id']) == str(course_id):
                course_code = c['code']
                course_name = c['name']
                break

        MOCK_NEXT_GRADE_ID += 1
        new_grade_item = {
            "id": MOCK_NEXT_GRADE_ID,
            "student_name": student_name,
            "student_id": student_id_str,
            "course_code": course_code,
            "course_name": course_name,
            "score": float(score),
            "grade": grade,
            "semester": semester
        }
        MOCK_GRADES.append(new_grade_item)
        
        # ALSO Save to the specific student's results for the Transcripts view
        if target_uid:
            if target_uid not in MOCK_RESULTS: MOCK_RESULTS[target_uid] = []
            MOCK_RESULTS[target_uid].append({
                "course": {"code": course_code, "name": course_name},
                "grade": grade, "score": float(score), "semester": semester
            })
            
        return jsonify({"message": "Grade submitted successfully"}), 201


# ---- All Students (for admin/lecturer) ----
@app.route('/api/students', methods=['GET'])
def get_all_students():
    if table_exists('students'):
        try:
            res = supabase.table('students').select('*').execute()
            return jsonify({"students": res.data}), 200
        except Exception as e:
            print(f"Supabase students error: {e}")

    students = [
        {**p, "user_id": uid}
        for uid, p in MOCK_PROFILES.items()
    ]
    return jsonify({"students": students}), 200


@app.route('/api/students/search', methods=['GET'])
def search_students():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"students": []}), 200

    if table_exists('students'):
        try:
            # Search by name or student_id
            res = supabase.table('students').select('*').or_(f"name.ilike.%{query}%,student_id.ilike.%{query}%").limit(10).execute()
            return jsonify({"students": res.data}), 200
        except Exception as e:
            print(f"Supabase search error: {e}")
            return jsonify({"error": str(e)}), 500

    # Mock search
    results = [
        {**p, "user_id": uid}
        for uid, p in MOCK_PROFILES.items()
        if query.lower() in p['name'].lower() or query.lower() in p['student_id'].lower()
    ]
    return jsonify({"students": results}), 200


@app.route('/api/admin/activity', methods=['GET'])
def get_activity():
    activity = []
    if table_exists('students'):
        try:
            # Latest 3 Students
            stus = supabase.table('students').select('name, created_at').order('created_at', desc=True).limit(3).execute()
            for s in stus.data:
                activity.append({"s": s['name'], "a": "New Registration", "t": s['created_at'][:10]})
            
            # Latest 3 Grades
            grades = supabase.table('results').select('*, students(name)').order('created_at', desc=True).limit(3).execute()
            for g in grades.data:
                name = g.get('students', {}).get('name', 'Student')
                activity.append({"s": name, "a": f"Grade Entered: {g['grade']}", "t": g['created_at'][:10]})
        except Exception as e:
            print(f"Activity error: {e}")

    if not activity:
        activity = [{"s": "System", "a": "No recent activity found", "t": "—"}]
    
    return jsonify({"activity": sorted(activity, key=lambda x: x['t'], reverse=True)[:5]}), 200


if __name__ == '__main__':
    app.run(debug=True, port=8000)
