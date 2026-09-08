"""Create a polished STA 332 Fall 2026 syllabus from the website copy."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "STA332-Fall-2026-Syllabus.pdf"
LOGO = ROOT / "img" / "logo.png"

PURPLE = colors.HexColor("#5E157D")
DARK_PURPLE = colors.HexColor("#3E0E55")
LAVENDER = colors.HexColor("#F3EDF7")
GOLD = colors.HexColor("#E6B94A")
INK = colors.HexColor("#24212A")
MUTED = colors.HexColor("#66616C")
RULE = colors.HexColor("#D8CFDC")
NOTE_BG = colors.HexColor("#F2F7FA")
NOTE_EDGE = colors.HexColor("#5D8293")
WARN_BG = colors.HexColor("#FFF6DE")
WARN_EDGE = colors.HexColor("#B47A00")


def fonts():
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    italic = Path("/System/Library/Fonts/Supplemental/Arial Italic.ttf")
    if regular.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("SyllabusSans", str(regular)))
        pdfmetrics.registerFont(TTFont("SyllabusSans-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("SyllabusSans-Italic", str(italic)))
        pdfmetrics.registerFontFamily(
            "SyllabusSans", normal="SyllabusSans", bold="SyllabusSans-Bold",
            italic="SyllabusSans-Italic", boldItalic="SyllabusSans-Bold",
        )
        return "SyllabusSans", "SyllabusSans-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = fonts()
BASE = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body", parent=BASE["BodyText"], fontName=FONT, fontSize=9.25,
    leading=13.1, textColor=INK, spaceAfter=6, allowWidows=0, allowOrphans=0,
)
SMALL = ParagraphStyle(
    "Small", parent=BODY, fontSize=8.25, leading=11.2, spaceAfter=4,
)
H1 = ParagraphStyle(
    "H1", parent=BASE["Heading1"], fontName=FONT_BOLD, fontSize=17,
    leading=20, textColor=PURPLE, spaceBefore=10, spaceAfter=5, keepWithNext=True,
)
H2 = ParagraphStyle(
    "H2", parent=BASE["Heading2"], fontName=FONT_BOLD, fontSize=11.5,
    leading=14, textColor=DARK_PURPLE, spaceBefore=9, spaceAfter=4, keepWithNext=True,
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, fontSize=9.1, leading=12.7, leftIndent=15,
    firstLineIndent=-9, bulletIndent=4, spaceAfter=3.5,
)
TABLE_TEXT = ParagraphStyle("TableText", parent=BODY, fontSize=8.25, leading=10.4, spaceAfter=0)
TABLE_HEAD = ParagraphStyle(
    "TableHead", parent=TABLE_TEXT, fontName=FONT_BOLD, textColor=colors.white,
)
CALLOUT = ParagraphStyle("Callout", parent=BODY, fontSize=8.8, leading=12.2, spaceAfter=3)


def p(text, style=BODY):
    return Paragraph(text, style)


def link(label, url):
    return f'<link href="{escape(url)}" color="#5E157D"><u>{escape(label)}</u></link>'


def bullet(text):
    return Paragraph(f"&bull;&nbsp; {text}", BULLET)


def heading(text):
    return [
        p(text, H1),
        HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=5),
    ]


def grid(data, widths, aligns=None, font_size=8.25):
    rows = []
    for row_number, row in enumerate(data):
        style = TABLE_HEAD if row_number == 0 else TABLE_TEXT
        cells = []
        for value in row:
            local = ParagraphStyle(f"table-{row_number}-{len(cells)}", parent=style)
            local.fontSize = font_size
            local.leading = font_size + 2.1
            cells.append(value if isinstance(value, Paragraph) else Paragraph(str(value), local))
        rows.append(cells)
    result = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LAVENDER]),
        ("GRID", (0, 0), (-1, -1), 0.45, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if aligns:
        for column, alignment in enumerate(aligns):
            commands.append(("ALIGN", (column, 0), (column, -1), alignment))
    result.setStyle(TableStyle(commands))
    return result


def callout(title, content, warning=False):
    items = content if isinstance(content, list) else [p(content, CALLOUT)]
    if title:
        title_style = ParagraphStyle(
            f"Callout-{title}", parent=CALLOUT, fontName=FONT_BOLD,
            textColor=WARN_EDGE if warning else NOTE_EDGE, spaceAfter=3,
        )
        items.insert(0, p(escape(title), title_style))
    result = Table([[items]], colWidths=[6.72 * inch], hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WARN_BG if warning else NOTE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, WARN_EDGE if warning else NOTE_EDGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(0.72 * inch, 10.33 * inch, 7.78 * inch, 10.33 * inch)
        canvas.setFont(FONT_BOLD, 8)
        canvas.setFillColor(PURPLE)
        canvas.drawString(0.75 * inch, 10.48 * inch, "STA 332 · Statistical Inference")
        canvas.setFont(FONT, 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(7.75 * inch, 10.48 * inch, "Fall 2026 · Duke University")
    canvas.setStrokeColor(RULE)
    canvas.line(0.72 * inch, 0.55 * inch, 7.78 * inch, 0.55 * inch)
    canvas.setFont(FONT, 7.6)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.36 * inch, "Based on the course website syllabus · Generated September 8, 2026")
    canvas.drawRightString(7.75 * inch, 0.36 * inch, str(doc.page))
    canvas.restoreState()


def build_story():
    s = []

    # Cover
    s.append(Spacer(1, 0.33 * inch))
    if LOGO.exists():
        logo = Image(str(LOGO), width=2 * inch, height=2 * inch)
        logo.hAlign = "CENTER"
        s.extend([logo, Spacer(1, 0.15 * inch)])
    cover = ParagraphStyle(
        "Cover", fontName=FONT_BOLD, fontSize=26, leading=30,
        textColor=PURPLE, alignment=TA_CENTER, spaceAfter=5,
    )
    subtitle = ParagraphStyle(
        "Subtitle", parent=BODY, fontSize=13, leading=17,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=8,
    )
    s.extend([
        p("STA 332", cover), p("Statistical Inference", cover),
        p("Fall 2026 · Duke University", subtitle), Spacer(1, 0.08 * inch),
        HRFlowable(width="62%", thickness=2, color=GOLD, hAlign="CENTER", spaceAfter=16),
    ])
    quick = grid(
        [["MEETS", "WHERE", "INSTRUCTOR"], ["Tue/Thu<br/>3:05-4:20 PM", "Gross Hall 103", "Anya Katsevich"]],
        [2.1 * inch] * 3, aligns=["CENTER"] * 3, font_size=9,
    )
    quick.hAlign = "CENTER"
    s.extend([quick, Spacer(1, 0.32 * inch)])
    cover_note = ParagraphStyle(
        "CoverNote", parent=BODY, fontSize=10, leading=14, textColor=MUTED,
        alignment=TA_CENTER, leftIndent=0.55 * inch, rightIndent=0.55 * inch,
    )
    s.append(p(
        "This PDF collects the Course Overview, Teaching Team, Course Materials, Assignments and Grading, "
        "Policies, and University Resources pages from the "
        + link("STA 332 course website", "https://anyakatsevich.github.io/sta332-f26/") + ".",
        cover_note,
    ))
    s.append(PageBreak())

    # Overview
    s.extend(heading("Course Overview"))
    s.append(p("Description", H2))
    s.append(p("This course provides an introduction to the mathematical foundation underlying statistical learning and inference. It introduces concepts and methods from the classical theory of statistics, with a focus on point estimation, interval estimation, and hypothesis testing, along with their adjacent topics and their application."))
    s.append(p("<b>Brief overview of topics.</b> Introduction to the problems of Statistical Inference. Definition of random sample, statistical model and likelihood. Definition and properties of estimators and sufficient and complete statistics. Point estimation: comparing estimators in decision theoretic framework (loss functions, risk, mean squared error) and optimality results (Uniform Minimum Variance Estimators, Fisher's information, Cramer's Rao Lower bound). Hypothesis testing: comparing testing procedures and constructing optimal tests within the Neyman-Pearson framework. Tests based on the likelihood ratio. Confidence intervals: construction based on inverting tests. Asymptotic considerations: consistent and asymptotically efficient estimators. Likelihood-based asymptotic tests and confidence intervals."))
    s.append(p("<b>Prerequisites:</b> (Statistical Science 240L, 230, or 231) and (Mathematics 202, 212, 219, or 222). Recommended prerequisite: Statistical Science 210, 360, and (Mathematics 221, 218, or 216). Specifically, students should be fluent in calculus (differentiation, integration, etc.), and probability (discrete and continuous random variables, joint, marginal and conditional distributions, etc). Familiarity with basic estimation concepts such as the maximum likelihood principle and Bayes rule is helpful."))
    s.append(p("Meetings", H2))
    s.append(grid([["Meeting", "Location", "Time"], ["Lecture", "Gross Hall 103", "Tue/Thu 3:05 PM - 4:20 PM"]], [1.3 * inch, 2.5 * inch, 2.9 * inch]))

    s.extend(heading("Teaching Team"))
    s.append(grid([
        ["Name", "Role", "Office Hours"],
        ["Gwen Jacobson", "Head TA", "Wed 6:00 PM - 7:00 PM, Old Chem 203B<br/>Fri 11:00 AM - 12:00 PM, Old Chem 203B"],
        ["Jun Chen", "TA", "Fri 5:00 PM - 7:00 PM, Old Chem 203B"],
        ["Varun Mittal", "TA", "Tue 8:30 AM - 10:30 AM, Old Chem 203B"],
        ["Bethany Akinola", "TA", "Mon 6:00 PM - 8:00 PM, Old Chem 203A"],
        ["Erin Chen", "TA", "Thu 5:30 PM - 6:30 PM, Old Chem 203B<br/>Fri 1:30 PM - 2:30 PM, Old Chem 203A"],
        ["Anya Katsevich", "Instructor", "Tue/Thu 4:45 PM - 5:45 PM, Old Chem 216"],
    ], [1.65 * inch, 1.1 * inch, 3.95 * inch]))

    s.extend(heading("Course Materials"))
    s.append(p("Textbooks", H2))
    s.append(p("You are not required to purchase a textbook for this class. However, if you wish to follow along with one, these are good options:"))
    s.extend([
        bullet("[DS] <i>Probability and Statistics</i> by Morris DeGroot and Mark Schervish;"),
        bullet("[Wass] <i>All of Statistics</i> by Larry Wasserman."),
        p("Another good source are these Berkeley " + link("notes", "https://stat210a.berkeley.edu/fall-2024/") + ". If a sign-in pop-up appears, just press \"Cancel\", and you will be able to access the website."),
        p("In the <b>PREPARE</b> column of the " + link("course schedule", "https://anyakatsevich.github.io/sta332-f26/") + ", I will indicate which parts of [DS], [Wass], or the Berkeley notes correspond to the lectures. My own lecture notes will be posted in the <b>MATERIALS</b> column; I will do my best to post them before lecture, but no guarantees."),
        p("Technology", H2),
        p("Lecture will largely be a low tech affair: pencil and paper will suffice. In general, you will need access to a device with internet so that you can use the following:"),
        bullet(link("This course page", "https://anyakatsevich.github.io/sta332-f26/") + " that you are on right now;"),
        bullet(link("Canvas", "https://go.canvas.duke.edu/") + ", through which you can access " + link("Gradescope", "https://www.gradescope.com/courses/82894") + " and " + link("Ed Discussion", "https://edstem.org/us/courses/103644/discussion") + ";"),
        bullet(link("Zoom", "https://duke.zoom.us/") + " (e.g. for remote office hours)."),
        p("If access to technology becomes a concern for you during the semester, contact the instructor immediately to discuss options."),
    ])

    # Grading
    s.extend(heading("Assignments and Grading"))
    s.append(p("Your final course grade will be calculated as follows:"))
    s.append(grid([
        ["Category", "Percentage"], ["Problem Sets", "10%"], ["Quizzes", "15%"],
        ["Midterm Exam 1", "25%"], ["Midterm Exam 2", "25%"], ["Final exam", "25%"],
    ], [4.5 * inch, 2.2 * inch], ["LEFT", "CENTER"]))
    s.extend([Spacer(1, 0.06 * inch), p("Your final letter grade will be determined based on the usual thresholds:")])
    s.append(grid([
        ["Grade", "Range", "Grade", "Range", "Grade", "Range"],
        ["A+", ">= 97", "B+", "87 - 89.99", "C+", "77 - 79.99"],
        ["A", "93 - 96.99", "B", "83 - 86.99", "C", "73 - 76.99"],
        ["A-", "90 - 92.99", "B-", "80 - 82.99", "C-", "70 - 72.99"],
        ["D+", "67 - 69.99", "D", "63 - 66.99", "D-", "60 - 62.99"],
        ["F", "< 60", "", "", "", ""],
    ], [0.62 * inch, 1.45 * inch] * 3, ["CENTER"] * 6))
    s.extend([Spacer(1, 0.07 * inch), callout(None, "These thresholds will not change, and they will be applied exactly. This means that the final grades will not be curved, and a 92.99, for example, will not be rounded up to an A.", True)])

    s.append(p("Problem Sets (10%)", H2))
    s.append(p("Mathematics is like everything else in life; if you practice, you improve. As such, I encourage you to take the problem sets seriously. Truly understanding how to solve the problems on each problem set is great preparation for the exams. Copying AI-generated solutions without understanding them will not help you learn! You must hand-write your solutions, either on paper or on a tablet, and upload them to " + link("Gradescope", "https://www.gradescope.com/courses/82894") + " by the due date as a single .pdf file."))
    s.append(p("<b>Grading scheme:</b> we will grade each problem set out of 10 points. 2 out of 10 points are awarded for completing every problem. The other 8 points are awarded for correctly solving one problem chosen by the teaching team. We will not disclose ahead of time which problem is graded, so you should solve them all."))
    s.append(grid([["Component", "Points"], ["Coherent attempt on every required problem", "2"], ["Sampled problem: correct, justified, clearly written", "8"]], [5.5 * inch, 1.2 * inch], ["LEFT", "CENTER"]))
    s.extend([Spacer(1, 0.07 * inch), callout("Grace", "Your lowest problem set score will be dropped at the end of the semester.")])

    s.append(p("Quizzes (15%)", H2))
    s.append(p("We will have six ten-minute in-class quizzes, which will be announced ahead of time. The quizzes are there to encourage you to engage with the material and study continually, rather than only right before the exams. I know quizzes can be stressful, so the grading policy will be generous."))
    s.append(p("Your final quiz grade is computed from your raw quiz average (your average score in percentage points across the six quizzes) as follows:"))
    eq = ParagraphStyle("Equation", parent=BODY, fontName=FONT_BOLD, fontSize=10.3, leading=15, alignment=TA_CENTER, textColor=DARK_PURPLE, backColor=LAVENDER, borderPadding=8, spaceAfter=7)
    s.append(p("Final quiz grade = min(100, 3/2 × Raw quiz average)", eq))
    s.append(p("For example, if each quiz has three questions and you get two correct on each one, then your raw quiz average is 66.67% and your final quiz grade is 100%."))
    s.append(callout("Missed quizzes", [
        p("No make-up quizzes will be given. If you miss a quiz, you get a zero for it by default, unless your absence is recognized by a Dean's Excuse, Notification of Varsity Athletic Participation, or Religious Observance Form; see the forms " + link("here", "https://trinity.duke.edu/undergraduate/academic-policies/class-attendance-and-missed-work#collapse-accordion-1072-2") + ".", CALLOUT),
        p("After the appropriate scores have been included, your raw quiz average will be converted to your final quiz grade using the above formula.", CALLOUT),
    ]))

    s.append(p("Exams (25% each)", H2))
    s.append(p("There will be three exams. The dates, times, and locations are firm, so mark your calendar now:"))
    s.extend([
        bullet("<b>Midterm 1:</b> Tuesday October 6 during lecture;"),
        bullet("<b>Midterm 2:</b> Thursday November 19 during lecture;"),
        bullet("<b>Final:</b> Thursday December 10 from 2 PM - 5 PM in Gross Hall 103."),
        p("These will be old school, pencil-and-paper, in-class exams. Exams are closed-book and closed-notes. No online or electronic resources are permitted."),
        p("If you seek testing accommodations, make sure the Student Disability Access Office sends me a letter, and then please make your appointments in the " + link("Testing Center", "https://testingcenter.duke.edu") + " as soon as possible."),
        callout("Grace", "If you do better on the final exam than you did on one of the midterms, we will replace your lowest midterm exam score with your final exam score."),
        Spacer(1, 0.06 * inch),
        callout("No make-up exams", "If you are absent from one of the midterms for whatever reason, there will not be a make-up. Pursuant to the above policy, we will simply replace the missed midterm score with the final exam score. If you miss the final exam, you get a zero unless you have a " + link("Dean's Excuse", "https://trinity.duke.edu/undergraduate/academic-policies/final-exams-scheduling-conflicts-and-absences") + ".", True),
    ])

    # Policies
    s.extend(heading("Policies"))
    s.append(p("Collaboration", H2))
    s.append(p("You are <i>enthusiastically encouraged</i> to work together and help one another on problem sets. However, copying someone else's solutions word-for-word is plagiarism, and all involved will earn a zero on the assignment and be referred to the conduct office, both sharers and recipients alike. The write-up you submit must be your own work."))
    s.append(p("Use of outside resources, including AI", H2))
    s.append(p("There are at least two reasons you might seek outside resources:"))
    s.extend([
        bullet("<b>Extra practice or alternative instruction:</b> Go crazy. Knock yourself out. Have a ball. The internet is saturated with good (and horrible) resources for learning this material, so if you find something that really resonates with you, have at it;"),
        bullet("<b>Doing the problems for you:</b> If you find a solution online, or ask a language model to generate one, and you copy it down and submit it as your own work, that is plagiarism. If we detect it, you will earn a zero for that part of your write-up."),
        p('"' + link("Using ChatGPT to complete assignments is like bringing a forklift into the weight room; you will never improve your cognitive fitness that way", "https://www.newyorker.com/culture/the-weekend-essay/why-ai-isnt-going-to-make-art") + '." Furthermore, 90% of your final course grade is determined by your performance on old school, no-tech exams. As such, outsourcing all of your <i>thinking</i> to an AI will probably end in humiliating disaster. To avoid this, I suggest you abstain from using language models to do the problems for you.'),
    ])
    s.append(p("Communication", H2))
    s.append(p("If you wish to ask content-related questions in writing, please do not do so via e-mail. Instead, please use the course discussion forum " + link("Ed Discussion", "https://edstem.org/us/courses/103644/discussion") + ". That way all members of the teaching team can see your question, and all students can benefit from the ensuing discussion. You are also encouraged to answer one another's questions."))
    s.append(p("If you have questions about personal matters that may not be appropriate for the public course forum (e.g. illness, accommodations, etc), then please e-mail the instructor directly (anya.katsevich@duke.edu)."))
    s.append(callout(None, "You can ask questions anonymously on Ed. The teaching team will still know your identity, but your peers will not."))
    s.append(p("Late work and extensions", H2))
    s.append(p("No late work will be accepted unless you request an extension in advance by e-mailing the instructor directly (anya.katsevich@duke.edu). All reasonable requests will be entertained, but extensions will not be long."))
    s.append(p("Regrade requests", H2))
    s.append(p("If you receive a graded assignment back, and you believe that some part of it was graded incorrectly, you may dispute the grade by submitting a " + link("regrade request", "https://guides.gradescope.com/hc/en-us/articles/21854736042253-Submitting-a-Regrade-Request") + " in Gradescope. Note the following:"))
    for item in [
        "You have one week after you receive a grade to submit a regrade request;",
        "You should submit separate regrade requests for each question you wish to dispute, not a single catch-all request;",
        "Requests will be considered if there was an error in the grade calculation or if a correct answer was mistakenly marked as incorrect;",
        "Requests to dispute the number of points deducted for an incorrect response will not be considered;",
        "<b>No grades will be changed after the final exam has been administered.</b>",
    ]:
        s.append(bullet(item))
    s.append(p("Attendance", H2))
    s.append(p("Live your life. Attendance is not strictly required for any of the class meetings, and the responsibility lies with us to make class meetings sufficiently engaging and informative that you choose to attend. Having said that, success in this class and regular attendance are probably highly positively correlated."))
    s.append(p("Accommodations", H2))
    s.append(p("If you need accommodations for this class, you will need to register with the Student Disability Access Office (SDAO) and provide them with documentation related to your needs. SDAO will work with you to determine what accommodations are appropriate for your situation. Please note that accommodations are not retroactive and disability accommodations cannot be provided until a Faculty Accommodation Letter has been given to me. Please contact SDAO for more information: sdao@duke.edu or access.duke.edu."))
    s.append(p("Duke Community Standard", H2))
    s.append(p("Duke University is a community dedicated to scholarship, leadership, and service and to the principles of honesty, fairness, respect, and accountability. Members of this community commit to reflect upon and uphold these principles in all academic and non-academic endeavors, and to protect and promote a culture of integrity."))
    s.append(p("Duke University has high expectations for students' scholarship and conduct. In accepting admission, students indicate their willingness to subscribe to and be governed by the rules and regulations of the university, which flow from the " + link("Duke Community Standard (DCS)", "https://dukecommunitystandard.students.duke.edu") + "."))
    s.append(p("Regardless of course delivery format, it is the responsibility of all students to understand and follow all Duke policies, including but not limited to the " + link("academic integrity policy", "https://dukecommunitystandard.students.duke.edu/policy/academic-dishonesty/") + " (e.g., completing one's own work, following proper citation of sources, adhering to guidance around group work projects, and more). Ignoring these requirements is a violation of the DCS."))
    s.append(p("Students can direct any questions or concerns regarding academic integrity to the Office of Student Conduct and Community Standards at conduct@duke.edu and can access the DCS guide at dukecommunitystandard.students.duke.edu."))
    s.append(p("In STA 332 specifically..."))
    s.extend([
        bullet("If a conduct violation results in a zero on a problem set, that zero will not be dropped;"),
        bullet("If a conduct violation results in a zero on a midterm, that zero will not be replaced with your final exam score;"),
        bullet("If we discover that students are sharing and copying assignment solutions, all students involved will be penalized equally, the sharers the same as the recipients."),
    ])

    # Resources
    s.extend(heading("University Resources"))
    s.append(p("Course costs", H2))
    s.append(p("If you are having difficulty with the costs associated with this course (obtaining a laptop, mostly), here are some resources:"))
    s.extend([
        bullet("<b>" + link("Karsh Office of Undergraduate Support", "https://financialaid.duke.edu/") + ":</b> Regardless of your aid package, Karsh offers loans and resources for connecting students with campus programs that might help alleviate course costs."),
        bullet("<b>" + link("DukeLIFE", "https://dukelife.duke.edu/programs/course-materials-assistance/") + ":</b> The Course Material Assistance program offers assistance for eligible students, including through the " + link("LIFE Loaner Laptop Program", "https://dukelife.duke.edu/academic-support/loaner-laptop-program/") + ". Students who are eligible for DukeLIFE benefits are notified before the start of the semester; program resources are limited."),
        bullet("<b>" + link("Duke Link", "https://link.duke.edu/") + ":</b> They have a small supply of laptops that can be rented out for five days at a time."),
    ])
    s.append(p("Tech support", H2))
    s.append(p("Contact the Duke OIT Service Desk at " + link("oit.duke.edu/help", "https://oit.duke.edu/help") + "."))
    s.append(p("Academic support", H2))
    s.append(p("There are times you may need help with the class that is beyond what can be provided by the teaching team. In those instances, I encourage you to visit the Academic Resource Center. The " + link("Academic Resource Center (the ARC)", "https://arc.duke.edu") + " offers services to support students academically during their undergraduate careers at Duke. The ARC can provide support with time management, academic skills and strategies, course-specific tutoring, and more. ARC services are available free to all Duke undergraduate student studying any discipline."))
    s.append(p("You can contact the Academic Resource Center by phone at (919) 684-5917, by email at theARC@duke.edu, or by visiting arc.duke.edu."))
    s.append(p("Accessibility", H2))
    s.append(p("If any portion of the course is not accessible to you due to challenges with technology or the course format, please let me know so we can make appropriate accommodations."))
    s.append(p("The " + link("Student Disability Access Office (SDAO)", "https://access.duke.edu/students") + " is available to ensure that students can engage with their courses and related assignments. Students should contact the SDAO to " + link("request or update accommodations", "https://access.duke.edu/requests") + " under these circumstances."))
    s.append(p("Mental health and well-being", H2))
    s.append(p("Duke is committed to holistic student wellbeing, which includes one's mental, emotional, and physical health. The university offers resources to help students manage daily stress, to encourage intentional self-care, and to access just-in-time support. If you find you need support, your mental and/or emotional health concerns are impacting your day-to-day activities, your academic performance, or you need someone to talk to, the resources below are available to you:"))
    s.extend([
        bullet("<b>" + link("DukeReach", "https://students.duke.edu/wellness/dukereach/") + ":</b> DukeReach provides comprehensive outreach services for students managing challenges related to mental health, physical health, social adjustment, and other stressors. Contact dukereach@duke.edu;"),
        bullet("<b>" + link("Counseling and Psychological Services (CAPS)", "https://students.duke.edu/wellness/caps/") + ":</b> CAPS offers counseling services to Duke students including virtual appointments and community referrals. Walk in or call 919-660-1000. Hours: Monday-Friday 9:00 AM - 4:00 PM. After-hours counseling: 919-660-1000 Option 2;"),
        bullet("<b>" + link("TimelyCare", "https://app.timelycare.com/auth/login") + ":</b> Free, confidential 24/7 mental health support through TalkNow and scheduled counseling;"),
        bullet("<b>" + link("Duke Student Health", "https://students.duke.edu/wellness/studenthealth/") + ":</b> Healthcare services for Duke students. Call 919-681-9355. Hours: Monday-Friday 8:00 AM - 4:30 PM; Thursday 9:00 AM - 4:30 PM. Closed 12:00-12:30 PM daily."),
    ])
    return s


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.72 * inch,
        title="STA 332 Fall 2026 Syllabus", author="Anya Katsevich",
        subject="Course syllabus for STA 332: Statistical Inference",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="syllabus", frames=[frame], onPage=header_footer)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
