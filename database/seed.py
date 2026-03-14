"""
Run this script once to populate the database with sample data.
Usage:  python database/seed.py
Demo credentials:
  Registration Number : CS2021001
  Parent Phone        : 9876543210
  OTP (simulated)     : printed to console
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.models import (
    db, Student, Attendance, Marks, CGPA, Backlog, Fee, Exam, Faculty
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ── Student ──────────────────────────────────────────────────────────────
    student = Student(
        reg_number="231FA04258",
        name="Arjun Sharma",
        branch="Computer Science and Engineering",
        year=3,
        current_semester=5,
        parent_phone="7671831151",
        class_advisor="Dr. Priya Mehta",
        advisor_email="priya.mehta@college.edu",
        advisor_phone="9988776655",
    )
    db.session.add(student)
    db.session.flush()  # get student.id

    # ── Attendance (Semester 5) ───────────────────────────────────────────────
    attendance_data = [
        ("Data Structures",          60, 52),
        ("Operating Systems",        55, 40),   # Low attendance (72.7%)
        ("Database Management",      58, 56),
        ("Computer Networks",        60, 45),   # Low attendance (75%)
        ("Software Engineering",     50, 48),
        ("Mathematics III",          48, 35),   # Low attendance (72.9%)
    ]
    for subject, total, attended in attendance_data:
        db.session.add(Attendance(
            student_id=student.id,
            subject=subject,
            total_classes=total,
            attended=attended,
            semester=5,
        ))

    # ── Marks (Semester 4 – completed) ───────────────────────────────────────
    marks_data = [
        ("Theory of Computation",  28, 62, 90,  100),
        ("Design & Analysis of Algorithms", 25, 50, 75, 100),
        ("Web Technologies",       30, 65, 95,  100),
        ("Digital Electronics",    20, 38, 58,  100),   # Backlog subject
        ("Microprocessors",        22, 42, 64,  100),
        ("Environmental Science",  27, 60, 87,  100),
    ]
    for subject, internal, external, total, max_m in marks_data:
        db.session.add(Marks(
            student_id=student.id,
            subject=subject,
            internal=internal,
            external=external,
            total=total,
            max_marks=max_m,
            semester=4,
        ))

    # ── CGPA ─────────────────────────────────────────────────────────────────
    cgpa_data = [
        (1, 7.8,  7.80),
        (2, 8.1,  7.95),
        (3, 7.6,  7.83),
        (4, 7.2,  7.68),
    ]
    for sem, sgpa, cgpa in cgpa_data:
        db.session.add(CGPA(
            student_id=student.id,
            semester=sem,
            sgpa=sgpa,
            cgpa=cgpa,
        ))

    # ── Backlogs ─────────────────────────────────────────────────────────────
    db.session.add(Backlog(
        student_id=student.id,
        subject="Digital Electronics",
        semester=4,
        status="pending",
    ))

    # ── Fees ─────────────────────────────────────────────────────────────────
    payment_history = json.dumps([
        {"date": "2024-07-15", "amount": 25000, "mode": "Online", "receipt": "REC001"},
        {"date": "2024-11-10", "amount": 25000, "mode": "DD",     "receipt": "REC002"},
    ])
    db.session.add(Fee(
        student_id=student.id,
        total_fees=120000.0,
        paid=50000.0,
        scholarship_amount=15000.0,
        scholarship_name="State Merit Scholarship",
        payment_history=payment_history,
    ))

    # ── Upcoming Exams ───────────────────────────────────────────────────────
    exams_data = [
        ("Data Structures",         "2026-03-20", "Internal",   "Unit III Internal Test"),
        ("Operating Systems",       "2026-03-22", "Internal",   "Unit III Internal Test"),
        ("Database Management",     "2026-03-18", "Assignment", "Mini Project Submission"),
        ("Computer Networks",       "2026-04-05", "Internal",   "Unit IV Internal Test"),
        ("Software Engineering",    "2026-03-25", "Assignment", "SRS Document Submission"),
        ("Mathematics III",         "2026-04-10", "External",   "End Semester Examination"),
    ]
    for subject, date, etype, desc in exams_data:
        db.session.add(Exam(
            student_id=student.id,
            subject=subject,
            exam_date=date,
            exam_type=etype,
            description=desc,
        ))

    # ── Faculty ──────────────────────────────────────────────────────────────
    faculty_data = [
        ("Data Structures",         "Prof. Ramesh Kumar",   "ramesh.kumar@college.edu",   "9001122334", "CSE"),
        ("Operating Systems",       "Dr. Sunita Rao",       "sunita.rao@college.edu",     "9001122335", "CSE"),
        ("Database Management",     "Prof. Anand Patel",    "anand.patel@college.edu",    "9001122336", "CSE"),
        ("Computer Networks",       "Dr. Meena Iyer",       "meena.iyer@college.edu",     "9001122337", "CSE"),
        ("Software Engineering",    "Prof. Vikram Singh",   "vikram.singh@college.edu",   "9001122338", "CSE"),
        ("Mathematics III",         "Dr. Kavitha Nair",     "kavitha.nair@college.edu",   "9001122339", "MATH"),
    ]
    for subject, name, email, phone, dept in faculty_data:
        db.session.add(Faculty(
            subject=subject,
            name=name,
            email=email,
            phone=phone,
            department=dept,
        ))

    # ══════════════════════════════════════════════════════════════════════════
    # STUDENT 2 – Priya Reddy (ECE)
    # ══════════════════════════════════════════════════════════════════════════
    student2 = Student(
        reg_number="231FA05112",
        name="Priya Reddy",
        branch="Electronics and Communication Engineering",
        year=3,
        current_semester=5,
        parent_phone="9988001122",
        class_advisor="Dr. Ramana Murthy",
        advisor_email="ramana.murthy@college.edu",
        advisor_phone="9876001122",
    )
    db.session.add(student2)
    db.session.flush()

    for subject, total, attended in [
        ("Signals and Systems",       58, 55),
        ("Analog Circuits",           60, 42),   # Low attendance
        ("Digital Signal Processing", 55, 50),
        ("VLSI Design",               50, 47),
        ("Electromagnetic Theory",    52, 38),   # Low attendance
        ("Control Systems",           48, 46),
    ]:
        db.session.add(Attendance(student_id=student2.id, subject=subject,
                                  total_classes=total, attended=attended, semester=5))

    for subject, internal, external, total, max_m in [
        ("Microcontrollers",       26, 58, 84, 100),
        ("Communication Systems",  22, 45, 67, 100),
        ("Network Analysis",       29, 63, 92, 100),
        ("Electronic Devices",     18, 30, 48, 100),   # Backlog
        ("Engineering Mathematics",25, 55, 80, 100),
        ("Environmental Science",  28, 60, 88, 100),
    ]:
        db.session.add(Marks(student_id=student2.id, subject=subject,
                             internal=internal, external=external,
                             total=total, max_marks=max_m, semester=4))

    for sem, sgpa, cgpa in [(1, 8.2, 8.20), (2, 7.9, 8.05), (3, 8.4, 8.17), (4, 7.5, 8.00)]:
        db.session.add(CGPA(student_id=student2.id, semester=sem, sgpa=sgpa, cgpa=cgpa))

    db.session.add(Backlog(student_id=student2.id, subject="Electronic Devices", semester=4, status="pending"))

    db.session.add(Fee(
        student_id=student2.id, total_fees=110000.0, paid=60000.0,
        scholarship_amount=10000.0, scholarship_name="Merit-cum-Means Scholarship",
        payment_history=json.dumps([
            {"date": "2024-08-01", "amount": 30000, "mode": "Online", "receipt": "REC101"},
            {"date": "2024-12-05", "amount": 30000, "mode": "Online", "receipt": "REC102"},
        ]),
    ))

    for subject, date, etype, desc in [
        ("Signals and Systems",       "2026-03-19", "Internal",   "Unit III Internal Test"),
        ("Analog Circuits",           "2026-03-21", "Internal",   "Unit III Internal Test"),
        ("Digital Signal Processing", "2026-03-26", "Assignment", "DSP Lab Project"),
        ("VLSI Design",               "2026-04-02", "Internal",   "Unit IV Internal Test"),
        ("Electromagnetic Theory",    "2026-04-08", "External",   "End Semester Examination"),
    ]:
        db.session.add(Exam(student_id=student2.id, subject=subject,
                            exam_date=date, exam_type=etype, description=desc))

    # ══════════════════════════════════════════════════════════════════════════
    # STUDENT 3 – Rahul Verma (ME)
    # ══════════════════════════════════════════════════════════════════════════
    student3 = Student(
        reg_number="231FA06075",
        name="Rahul Verma",
        branch="Mechanical Engineering",
        year=3,
        current_semester=5,
        parent_phone="8899776655",
        class_advisor="Prof. Suresh Babu",
        advisor_email="suresh.babu@college.edu",
        advisor_phone="9871234567",
    )
    db.session.add(student3)
    db.session.flush()

    for subject, total, attended in [
        ("Thermodynamics",          60, 58),
        ("Fluid Mechanics",         55, 50),
        ("Machine Design",          58, 44),   # Low attendance
        ("Manufacturing Processes", 52, 49),
        ("Heat Transfer",           50, 46),
        ("Engineering Drawing",     48, 48),
    ]:
        db.session.add(Attendance(student_id=student3.id, subject=subject,
                                  total_classes=total, attended=attended, semester=5))

    for subject, internal, external, total, max_m in [
        ("Strength of Materials",  27, 60, 87, 100),
        ("Kinematics of Machinery",24, 52, 76, 100),
        ("Material Science",       30, 65, 95, 100),
        ("Workshop Technology",    26, 54, 80, 100),
        ("Engineering Mathematics",20, 40, 60, 100),
        ("Environmental Science",  28, 58, 86, 100),
    ]:
        db.session.add(Marks(student_id=student3.id, subject=subject,
                             internal=internal, external=external,
                             total=total, max_marks=max_m, semester=4))

    for sem, sgpa, cgpa in [(1, 7.5, 7.50), (2, 7.8, 7.65), (3, 7.3, 7.53), (4, 7.9, 7.63)]:
        db.session.add(CGPA(student_id=student3.id, semester=sem, sgpa=sgpa, cgpa=cgpa))

    db.session.add(Fee(
        student_id=student3.id, total_fees=100000.0, paid=75000.0,
        scholarship_amount=0.0, scholarship_name=None,
        payment_history=json.dumps([
            {"date": "2024-07-20", "amount": 50000, "mode": "Online", "receipt": "REC201"},
            {"date": "2024-11-15", "amount": 25000, "mode": "DD",     "receipt": "REC202"},
        ]),
    ))

    for subject, date, etype, desc in [
        ("Thermodynamics",          "2026-03-18", "Internal",   "Unit III Internal Test"),
        ("Fluid Mechanics",         "2026-03-24", "Assignment", "CFD Lab Report"),
        ("Machine Design",          "2026-04-01", "Internal",   "Unit IV Internal Test"),
        ("Heat Transfer",           "2026-04-10", "External",   "End Semester Examination"),
    ]:
        db.session.add(Exam(student_id=student3.id, subject=subject,
                            exam_date=date, exam_type=etype, description=desc))

    # ══════════════════════════════════════════════════════════════════════════
    # STUDENT 4 – Sneha Patil (IT)
    # ══════════════════════════════════════════════════════════════════════════
    student4 = Student(
        reg_number="231FA07190",
        name="Sneha Patil",
        branch="Information Technology",
        year=3,
        current_semester=5,
        parent_phone="7766554433",
        class_advisor="Dr. Anjali Deshmukh",
        advisor_email="anjali.deshmukh@college.edu",
        advisor_phone="9845671234",
    )
    db.session.add(student4)
    db.session.flush()

    for subject, total, attended in [
        ("Cloud Computing",         55, 53),
        ("Machine Learning",        60, 58),
        ("Cyber Security",          52, 40),   # Low attendance
        ("Software Testing",        50, 48),
        ("Web Development",         58, 57),
        ("Discrete Mathematics",    48, 44),
    ]:
        db.session.add(Attendance(student_id=student4.id, subject=subject,
                                  total_classes=total, attended=attended, semester=5))

    for subject, internal, external, total, max_m in [
        ("Java Programming",       30, 68, 98, 100),
        ("Computer Architecture",  25, 55, 80, 100),
        ("Data Mining",            28, 60, 88, 100),
        ("Operating Systems",      26, 52, 78, 100),
        ("Probability & Statistics",22, 48, 70, 100),
        ("Technical Communication",29, 62, 91, 100),
    ]:
        db.session.add(Marks(student_id=student4.id, subject=subject,
                             internal=internal, external=external,
                             total=total, max_marks=max_m, semester=4))

    for sem, sgpa, cgpa in [(1, 8.5, 8.50), (2, 8.8, 8.65), (3, 8.3, 8.53), (4, 8.6, 8.55)]:
        db.session.add(CGPA(student_id=student4.id, semester=sem, sgpa=sgpa, cgpa=cgpa))

    db.session.add(Fee(
        student_id=student4.id, total_fees=115000.0, paid=115000.0,
        scholarship_amount=20000.0, scholarship_name="University Topper Scholarship",
        payment_history=json.dumps([
            {"date": "2024-07-10", "amount": 55000, "mode": "Online", "receipt": "REC301"},
            {"date": "2024-10-20", "amount": 60000, "mode": "Online", "receipt": "REC302"},
        ]),
    ))

    for subject, date, etype, desc in [
        ("Cloud Computing",     "2026-03-20", "Assignment", "AWS Lab Project"),
        ("Machine Learning",    "2026-03-23", "Internal",   "Unit III Internal Test"),
        ("Cyber Security",      "2026-04-01", "Internal",   "Unit IV Internal Test"),
        ("Web Development",     "2026-03-28", "Assignment", "Full-Stack Project Demo"),
        ("Discrete Mathematics","2026-04-12", "External",   "End Semester Examination"),
    ]:
        db.session.add(Exam(student_id=student4.id, subject=subject,
                            exam_date=date, exam_type=etype, description=desc))

    # ══════════════════════════════════════════════════════════════════════════
    # STUDENT 5 – Karthik Nair (CSE)
    # ══════════════════════════════════════════════════════════════════════════
    student5 = Student(
        reg_number="231FA04310",
        name="Karthik Nair",
        branch="Computer Science and Engineering",
        year=3,
        current_semester=5,
        parent_phone="9123456780",
        class_advisor="Dr. Priya Mehta",
        advisor_email="priya.mehta@college.edu",
        advisor_phone="9988776655",
    )
    db.session.add(student5)
    db.session.flush()

    for subject, total, attended in [
        ("Data Structures",          60, 35),   # Very low attendance
        ("Operating Systems",        55, 30),   # Very low attendance
        ("Database Management",      58, 40),   # Low attendance
        ("Computer Networks",        60, 55),
        ("Software Engineering",     50, 42),
        ("Mathematics III",          48, 32),   # Very low attendance
    ]:
        db.session.add(Attendance(student_id=student5.id, subject=subject,
                                  total_classes=total, attended=attended, semester=5))

    for subject, internal, external, total, max_m in [
        ("Theory of Computation",  15, 30, 45, 100),   # Backlog
        ("Design & Analysis of Algorithms", 20, 35, 55, 100),
        ("Web Technologies",       22, 40, 62, 100),
        ("Digital Electronics",    12, 25, 37, 100),   # Backlog
        ("Microprocessors",        18, 38, 56, 100),
        ("Environmental Science",  25, 50, 75, 100),
    ]:
        db.session.add(Marks(student_id=student5.id, subject=subject,
                             internal=internal, external=external,
                             total=total, max_marks=max_m, semester=4))

    for sem, sgpa, cgpa in [(1, 6.2, 6.20), (2, 5.8, 6.00), (3, 6.5, 6.17), (4, 5.5, 6.00)]:
        db.session.add(CGPA(student_id=student5.id, semester=sem, sgpa=sgpa, cgpa=cgpa))

    db.session.add(Backlog(student_id=student5.id, subject="Theory of Computation", semester=4, status="pending"))
    db.session.add(Backlog(student_id=student5.id, subject="Digital Electronics", semester=4, status="pending"))

    db.session.add(Fee(
        student_id=student5.id, total_fees=120000.0, paid=40000.0,
        scholarship_amount=0.0, scholarship_name=None,
        payment_history=json.dumps([
            {"date": "2024-08-10", "amount": 40000, "mode": "DD", "receipt": "REC401"},
        ]),
    ))

    for subject, date, etype, desc in [
        ("Data Structures",         "2026-03-20", "Internal",   "Unit III Internal Test"),
        ("Operating Systems",       "2026-03-22", "Internal",   "Unit III Internal Test"),
        ("Database Management",     "2026-03-18", "Assignment", "Mini Project Submission"),
        ("Computer Networks",       "2026-04-05", "Internal",   "Unit IV Internal Test"),
        ("Mathematics III",         "2026-04-10", "External",   "End Semester Examination"),
    ]:
        db.session.add(Exam(student_id=student5.id, subject=subject,
                            exam_date=date, exam_type=etype, description=desc))

    db.session.commit()
    print("=" * 55)
    print("  Database seeded successfully!")
    print("=" * 55)
    print("  Demo Login Credentials:")
    print("  1. Reg: 231FA04258  Phone: 7671831151  (Arjun – CSE)")
    print("  2. Reg: 231FA05112  Phone: 9988001122  (Priya – ECE)")
    print("  3. Reg: 231FA06075  Phone: 8899776655  (Rahul – ME)")
    print("  4. Reg: 231FA07190  Phone: 7766554433  (Sneha – IT)")
    print("  5. Reg: 231FA04310  Phone: 9123456780  (Karthik – CSE)")
    print("=" * 55)
