import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load credentials
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

def seed():
    print("Starting database seed...")

    # 1. Seed Users
    users = [
        {"email": "admin@cavendish.ac.ug", "password": "admin", "name": "System Admin", "role": "admin"},
        {"email": "registry@cavendish.ac.ug", "password": "registry", "name": "Registry Officer", "role": "registry"},
        {"email": "finance@cavendish.ac.ug", "password": "finance", "name": "Finance Officer", "role": "finance"},
        {"email": "lecturer@cavendish.ac.ug", "password": "lecturer", "name": "Dr. Mukasa", "role": "lecturer"},
        {"email": "student@cavendish.ac.ug", "password": "student", "name": "Jane Doe", "role": "student"},
        {"email": "john@cavendish.ac.ug", "password": "student", "name": "John Smith", "role": "student"}
    ]
    
    for u in users:
        try:
            supabase.table("users").upsert(u, on_conflict="email").execute()
            print(f"User {u['email']} upserted.")
        except Exception as e:
            print(f"Error upserting user {u['email']}: {e}")

    # Get User IDs for reference
    user_res = supabase.table("users").select("id, email").execute()
    user_map = {u['email']: u['id'] for u in user_res.data}

    # 2. Seed Students
    students = [
        {
            "user_id": user_map.get("student@cavendish.ac.ug"),
            "student_id": "CU-2026-001",
            "name": "Jane Doe",
            "email": "student@cavendish.ac.ug",
            "phone": "+256 700 000000",
            "faculty": "Computer Science",
            "program": "BSc Computer Science",
            "year_of_study": 2
        },
        {
            "user_id": user_map.get("john@cavendish.ac.ug"),
            "student_id": "CU-2026-002",
            "name": "John Smith",
            "email": "john@cavendish.ac.ug",
            "phone": "+256 700 111111",
            "faculty": "Business Administration",
            "program": "BBA",
            "year_of_study": 1
        }
    ]

    for s in students:
        try:
            supabase.table("students").upsert(s, on_conflict="student_id").execute()
            print(f"Student {s['name']} upserted.")
        except Exception as e:
            print(f"Error upserting student {s['name']}: {e}")

    # 3. Seed Courses
    courses = [
        {"code": "CS101", "name": "Introduction to Programming", "credits": 3, "faculty": "Computer Science", "semester": "Semester 1"},
        {"code": "CS102", "name": "Data Structures & Algorithms", "credits": 4, "faculty": "Computer Science", "semester": "Semester 1"},
        {"code": "CS201", "name": "Database Systems", "credits": 3, "faculty": "Computer Science", "semester": "Semester 2"},
        {"code": "CS202", "name": "Web Development", "credits": 3, "faculty": "Computer Science", "semester": "Semester 2"},
        {"code": "MTH101", "name": "Calculus I", "credits": 3, "faculty": "Science", "semester": "Semester 1"},
        {"code": "BBA101", "name": "Principles of Management", "credits": 3, "faculty": "Business Administration", "semester": "Semester 1"},
        {"code": "BBA102", "name": "Financial Accounting", "credits": 3, "faculty": "Business Administration", "semester": "Semester 1"}
    ]

    for c in courses:
        try:
            supabase.table("courses").upsert(c, on_conflict="code").execute()
            print(f"Course {c['code']} upserted.")
        except Exception as e:
            print(f"Error upserting course {c['code']}: {e}")

    print("Seed complete!")

if __name__ == "__main__":
    seed()
