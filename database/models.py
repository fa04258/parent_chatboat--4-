from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    reg_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    current_semester = db.Column(db.Integer, nullable=False)
    parent_phone = db.Column(db.String(15), nullable=False)
    class_advisor = db.Column(db.String(100))
    advisor_email = db.Column(db.String(100))
    advisor_phone = db.Column(db.String(15))

    attendance = db.relationship("Attendance", backref="student", lazy=True)
    marks = db.relationship("Marks", backref="student", lazy=True)
    cgpa_records = db.relationship("CGPA", backref="student", lazy=True)
    backlogs = db.relationship("Backlog", backref="student", lazy=True)
    fees = db.relationship("Fee", backref="student", lazy=True, uselist=False)
    exams = db.relationship("Exam", backref="student", lazy=True)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    total_classes = db.Column(db.Integer, nullable=False)
    attended = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0.0
        return round((self.attended / self.total_classes) * 100, 2)


class Marks(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    internal = db.Column(db.Float, nullable=False)
    external = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, default=100.0)
    semester = db.Column(db.Integer, nullable=False)

    @property
    def grade(self):
        pct = (self.total / self.max_marks) * 100
        if pct >= 90: return "O"
        if pct >= 80: return "A+"
        if pct >= 70: return "A"
        if pct >= 60: return "B+"
        if pct >= 50: return "B"
        if pct >= 40: return "C"
        return "F"


class CGPA(db.Model):
    __tablename__ = "cgpa"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    sgpa = db.Column(db.Float, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)


class Backlog(db.Model):
    __tablename__ = "backlogs"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending / cleared / repeated


class Fee(db.Model):
    __tablename__ = "fees"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    total_fees = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Float, nullable=False)
    scholarship_amount = db.Column(db.Float, default=0.0)
    scholarship_name = db.Column(db.String(100))
    payment_history = db.Column(db.Text)  # JSON string

    @property
    def pending(self):
        return round(self.total_fees - self.paid - self.scholarship_amount, 2)


class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.String(20), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Internal / External / Assignment
    description = db.Column(db.String(200))


class Faculty(db.Model):
    __tablename__ = "faculty"
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50))


class StudentContact(db.Model):
    """Extra contact numbers for a student (parent, guardian, emergency)."""
    __tablename__ = "student_contacts"
    id           = db.Column(db.Integer, primary_key=True)
    student_id   = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    phone        = db.Column(db.String(15), nullable=False)
    contact_type = db.Column(db.String(20), default="parent")   # parent / guardian / emergency
    is_primary   = db.Column(db.Boolean,  default=False)

    student = db.relationship("Student", backref="contacts")


class OTPStore(db.Model):
    __tablename__ = "otp_store"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
