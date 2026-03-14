"""
Rule-based intent handler for the Parent Chatbot.
Each intent is matched via keyword sets and returns a formatted HTML/text reply.
"""
import json
from database.models import db, Student, Attendance, Marks, CGPA, Backlog, Fee, Exam, Faculty
from deep_translator import GoogleTranslator


def _to_english(text: str) -> str:
    """Translate any non-English input to English for intent matching."""
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception:
        return text  # Fall back to original on failure

# ── Intent keyword map ────────────────────────────────────────────────────────
INTENT_MAP = {
    "attendance_overall":   ["overall attendance", "total attendance", "attendance percentage", "attendance %"],
    "attendance_subject":   ["subject attendance", "subject wise attendance", "attendance by subject", "attendance subject"],
    "attendance_low":       ["low attendance", "short attendance", "attendance alert", "attendance warning", "detained"],
    "academic_status":      ["backlog", "backlogs", "arrear", "arrears", "failed", "repeated subject", "incomplete", "course completion", "academic status"],
    "marks":                ["marks", "score", "result", "grades", "subject marks", "subject score", "performance"],
    "cgpa_current":         ["cgpa", "gpa", "current cgpa", "latest cgpa"],
    "cgpa_semester":        ["semester cgpa", "sgpa", "semester wise cgpa", "semester gpa"],
    "cgpa_year":            ["year cgpa", "year wise cgpa", "annual cgpa"],
    "exams":                ["exam", "examination", "test", "assignment", "deadline", "schedule", "calendar", "upcoming"],
    "fees":                 ["fee", "fees", "payment", "pending fee", "scholarship", "financial", "paid", "due"],
    "faculty":              ["faculty", "teacher", "professor", "contact", "staff", "class advisor", "advisor", "office"],
    "insights":             ["insight", "strong subject", "weak subject", "improvement", "suggestion", "performance insight", "analysis"],
    "help":                 ["help", "menu", "what can you do", "options", "commands", "hi", "hello", "hey", "start"],
    "student_info":         ["student info", "student details", "profile", "who is", "student name", "my child"],
}


def _match_intent(message: str) -> str:
    msg = message.lower().strip()
    for intent, keywords in INTENT_MAP.items():
        for kw in keywords:
            if kw in msg:
                return intent
    return "unknown"


# ── Response builders ─────────────────────────────────────────────────────────

def _fmt_table(headers: list, rows: list) -> str:
    """Build a simple HTML table."""
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
    return f'<table class="info-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def handle_message(message: str, student_id: int) -> dict:
    """
    Main entry point. Returns dict with keys:
      - reply  : HTML string shown in chat
      - intent : matched intent (for debugging)
    """
    student = db.session.get(Student, student_id)
    if not student:
        return {"reply": "Session error. Please log in again.", "intent": "error"}

    # Translate message to English so intent keywords always match
    english_message = _to_english(message)
    intent = _match_intent(english_message)

    handlers = {
        "help":               _help,
        "student_info":       _student_info,
        "attendance_overall": _attendance_overall,
        "attendance_subject": _attendance_subject,
        "attendance_low":     _attendance_low,
        "academic_status":    _academic_status,
        "marks":              _marks,
        "cgpa_current":       _cgpa_current,
        "cgpa_semester":      _cgpa_semester,
        "cgpa_year":          _cgpa_year,
        "exams":              _exams,
        "fees":               _fees,
        "faculty":            _faculty,
        "insights":           _insights,
    }

    fn = handlers.get(intent, _unknown)
    reply = fn(student)
    return {"reply": reply, "intent": intent}


# ── Individual handlers ───────────────────────────────────────────────────────

def _help(student: Student) -> str:
    return (
        f"<b>👋 Hello! I'm your Academic Assistant for {student.name}.</b><br><br>"
        "You can ask me about:<br>"
        "<ul>"
        "<li>📊 <b>Attendance</b> – overall, subject-wise, low attendance alerts</li>"
        "<li>📝 <b>Marks</b> – subject-wise marks &amp; grades</li>"
        "<li>🎓 <b>CGPA</b> – current, semester-wise, year-wise</li>"
        "<li>⚠️ <b>Backlogs</b> – arrears / academic status</li>"
        "<li>📅 <b>Exams</b> – upcoming tests &amp; assignment deadlines</li>"
        "<li>💰 <b>Fees</b> – payment status, pending amount, scholarship</li>"
        "<li>👨‍🏫 <b>Faculty</b> – teacher contacts &amp; class advisor details</li>"
        "<li>💡 <b>Insights</b> – strong/weak subjects &amp; improvement tips</li>"
        "<li>🎒 <b>Student Info</b> – profile &amp; enrollment details</li>"
        "</ul>"
        "Just type your question naturally! E.g. <i>\"What is the overall attendance?\"</i>"
    )


def _student_info(student: Student) -> str:
    rows = [
        ("Name", student.name),
        ("Registration Number", student.reg_number),
        ("Branch", student.branch),
        ("Year", student.year),
        ("Current Semester", student.current_semester),
        ("Class Advisor", student.class_advisor or "N/A"),
    ]
    table = _fmt_table(["Field", "Details"], rows)
    return f"<b>🎒 Student Profile</b><br>{table}"


def _attendance_overall(student: Student) -> str:
    records = Attendance.query.filter_by(student_id=student.id, semester=student.current_semester).all()
    if not records:
        return "No attendance records found for the current semester."
    total_classes = sum(r.total_classes for r in records)
    total_attended = sum(r.attended for r in records)
    overall = round((total_attended / total_classes) * 100, 2) if total_classes else 0
    color = "green" if overall >= 75 else "red"
    return (
        f"<b>📊 Overall Attendance – Semester {student.current_semester}</b><br>"
        f"Classes Attended: <b>{total_attended}</b> / {total_classes}<br>"
        f"Overall Percentage: <b style='color:{color}'>{overall}%</b><br>"
        + ("<span style='color:red'>⚠️ Attendance is below 75%! Risk of shortage.</span>" if overall < 75 else
           "<span style='color:green'>✅ Attendance is satisfactory.</span>")
    )


def _attendance_subject(student: Student) -> str:
    records = Attendance.query.filter_by(student_id=student.id, semester=student.current_semester).all()
    if not records:
        return "No subject-wise attendance data available."
    rows = []
    for r in records:
        pct = r.percentage
        status = "✅" if pct >= 75 else "⚠️ Low"
        rows.append((r.subject, r.attended, r.total_classes, f"{pct}%", status))
    table = _fmt_table(["Subject", "Attended", "Total", "Percentage", "Status"], rows)
    return f"<b>📚 Subject-wise Attendance – Semester {student.current_semester}</b><br>{table}"


def _attendance_low(student: Student) -> str:
    records = Attendance.query.filter_by(student_id=student.id, semester=student.current_semester).all()
    low = [r for r in records if r.percentage < 75]
    if not low:
        return "<span style='color:green'>✅ No low attendance alerts. All subjects are above 75%.</span>"
    rows = [(r.subject, f"{r.percentage}%", r.attended, r.total_classes) for r in low]
    table = _fmt_table(["Subject", "Percentage", "Attended", "Total"], rows)
    return (
        f"<b>⚠️ Low Attendance Alert – Semester {student.current_semester}</b><br>"
        f"<span style='color:red'>{len(low)} subject(s) below 75%:</span><br>{table}"
        "<br><i>Please ensure regular attendance to avoid detention from exams.</i>"
    )


def _academic_status(student: Student) -> str:
    backlogs = Backlog.query.filter_by(student_id=student.id).all()
    pending = [b for b in backlogs if b.status == "pending"]
    cleared = [b for b in backlogs if b.status == "cleared"]

    if not backlogs:
        status_msg = "<span style='color:green'>✅ No backlogs. Course is on track.</span>"
    else:
        rows = [(b.subject, f"Semester {b.semester}", b.status.capitalize()) for b in backlogs]
        table = _fmt_table(["Subject", "Semester", "Status"], rows)
        status_msg = f"<span style='color:red'>⚠️ {len(pending)} pending backlog(s):</span><br>{table}"

    return (
        f"<b>📋 Academic Status</b><br>"
        f"Total Backlogs: <b>{len(backlogs)}</b> | "
        f"Pending: <b>{len(pending)}</b> | "
        f"Cleared: <b>{len(cleared)}</b><br><br>"
        + status_msg
    )


def _marks(student: Student) -> str:
    records = Marks.query.filter_by(student_id=student.id, semester=4).all()
    if not records:
        return "No marks records found."
    rows = [(r.subject, r.internal, r.external, r.total, f"{r.total}/{r.max_marks}", r.grade) for r in records]
    table = _fmt_table(["Subject", "Internal", "External", "Total", "Score", "Grade"], rows)
    return f"<b>📝 Subject-wise Marks – Semester 4</b><br>{table}"


def _cgpa_current(student: Student) -> str:
    latest = (
        CGPA.query.filter_by(student_id=student.id)
        .order_by(CGPA.semester.desc())
        .first()
    )
    if not latest:
        return "No CGPA records found."
    color = "green" if latest.cgpa >= 7.0 else ("orange" if latest.cgpa >= 5.5 else "red")
    return (
        f"<b>🎓 Current Academic Performance</b><br>"
        f"Latest Semester: <b>Semester {latest.semester}</b><br>"
        f"SGPA: <b>{latest.sgpa}</b><br>"
        f"CGPA: <b style='color:{color}'>{latest.cgpa}</b>"
    )


def _cgpa_semester(student: Student) -> str:
    records = CGPA.query.filter_by(student_id=student.id).order_by(CGPA.semester).all()
    if not records:
        return "No CGPA records found."
    rows = [(f"Semester {r.semester}", r.sgpa, r.cgpa) for r in records]
    table = _fmt_table(["Semester", "SGPA", "CGPA"], rows)
    return f"<b>📈 Semester-wise CGPA</b><br>{table}"


def _cgpa_year(student: Student) -> str:
    records = CGPA.query.filter_by(student_id=student.id).order_by(CGPA.semester).all()
    if not records:
        return "No CGPA records found."
    year_data = {}
    for r in records:
        yr = (r.semester + 1) // 2
        year_data.setdefault(yr, []).append(r)

    rows = []
    for yr, recs in sorted(year_data.items()):
        avg_sgpa = round(sum(r.sgpa for r in recs) / len(recs), 2)
        end_cgpa = recs[-1].cgpa
        rows.append((f"Year {yr}", avg_sgpa, end_cgpa))

    table = _fmt_table(["Year", "Avg SGPA", "CGPA at Year End"], rows)
    return f"<b>📅 Year-wise Academic Performance</b><br>{table}"


def _exams(student: Student) -> str:
    records = Exam.query.filter_by(student_id=student.id).order_by(Exam.exam_date).all()
    if not records:
        return "No upcoming exams or assignments found."
    rows = [(r.subject, r.exam_type, r.exam_date, r.description or "") for r in records]
    table = _fmt_table(["Subject", "Type", "Date", "Description"], rows)
    return f"<b>📅 Upcoming Exams &amp; Deadlines</b><br>{table}"


def _fees(student: Student) -> str:
    fee = Fee.query.filter_by(student_id=student.id).first()
    if not fee:
        return "No fee records found."

    history_html = ""
    if fee.payment_history:
        try:
            history = json.loads(fee.payment_history)
            rows = [(p["date"], f"₹{p['amount']:,}", p["mode"], p["receipt"]) for p in history]
            history_html = "<br><b>Payment History:</b><br>" + _fmt_table(
                ["Date", "Amount", "Mode", "Receipt"], rows
            )
        except (json.JSONDecodeError, KeyError):
            pass

    pending_color = "red" if fee.pending > 0 else "green"
    scholarship_info = (
        f"<br>🏅 Scholarship: <b>{fee.scholarship_name}</b> – ₹{fee.scholarship_amount:,.0f}"
        if fee.scholarship_amount > 0 else ""
    )

    return (
        f"<b>💰 Fee Status</b><br>"
        f"Total Fees: <b>₹{fee.total_fees:,.0f}</b><br>"
        f"Amount Paid: <b style='color:green'>₹{fee.paid:,.0f}</b><br>"
        f"Pending Amount: <b style='color:{pending_color}'>₹{fee.pending:,.0f}</b>"
        + scholarship_info
        + history_html
    )


def _faculty(student: Student) -> str:
    faculty_list = Faculty.query.all()
    advisor_info = (
        f"<b>👨‍🏫 Class Advisor:</b> {student.class_advisor}<br>"
        f"📧 {student.advisor_email} | 📞 {student.advisor_phone}<br><br>"
    )
    rows = [(f.subject, f.name, f.email or "N/A", f.phone or "N/A") for f in faculty_list]
    table = _fmt_table(["Subject", "Faculty Name", "Email", "Phone"], rows)
    return advisor_info + f"<b>👩‍🏫 Subject Faculty Contacts</b><br>{table}"


def _insights(student: Student) -> str:
    records = Marks.query.filter_by(student_id=student.id, semester=4).all()
    if not records:
        return "No performance data available for insights."

    sorted_by_pct = sorted(records, key=lambda r: r.total / r.max_marks, reverse=True)
    strong = sorted_by_pct[:2]
    weak = sorted_by_pct[-2:]

    strong_str = ", ".join(f"<b>{r.subject}</b> ({r.grade})" for r in strong)
    weak_str = ", ".join(f"<b>{r.subject}</b> ({r.grade})" for r in weak)

    att_records = Attendance.query.filter_by(student_id=student.id, semester=student.current_semester).all()
    low_att = [r.subject for r in att_records if r.percentage < 75]
    att_suggestion = (
        f"<li>⚠️ Attendance in <b>{', '.join(low_att)}</b> is below 75%. Attend regularly to avoid exam restrictions.</li>"
        if low_att else "<li>✅ Attendance is satisfactory in all subjects.</li>"
    )

    backlogs = Backlog.query.filter_by(student_id=student.id, status="pending").all()
    backlog_suggestion = (
        f"<li>📚 Clear pending backlog in <b>{', '.join(b.subject for b in backlogs)}</b> before next semester.</li>"
        if backlogs else "<li>✅ No pending backlogs.</li>"
    )

    return (
        f"<b>💡 Performance Insights</b><br><br>"
        f"🌟 <b>Strong Subjects:</b> {strong_str}<br>"
        f"📉 <b>Needs Improvement:</b> {weak_str}<br><br>"
        f"<b>Recommendations:</b><ul>"
        + att_suggestion
        + backlog_suggestion +
        "<li>📖 Focus on weak subjects with additional practice and faculty guidance.</li>"
        "<li>🎯 Aim to improve CGPA in the upcoming semester.</li>"
        "</ul>"
    )


def _unknown(student: Student) -> str:
    return (
        "I didn't quite understand that. Here are some things you can ask:<br>"
        "<i>attendance, marks, CGPA, backlogs, exams, fees, faculty, insights</i><br>"
        "Or type <b>help</b> to see all options."
    )
