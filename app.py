import os
from io import BytesIO
from datetime import date
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

APP_TITLE = "Natural Shrimp Aquaculture LLC — Job Request"
DATA_FILE = "job_requests_history.csv"
BLUE = colors.HexColor("#315F91")   # close to the blue ink/header in the reference
INK = colors.HexColor("#202B38")
RULE = colors.HexColor("#687887")

st.set_page_config(page_title=APP_TITLE, layout="wide")

def register_fonts():
    """Use an installed Unicode font when available; PDF still works without it."""
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", "Liberation"),
    ]
    for path, name in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                pass
    return "Helvetica"

PDF_FONT = register_fonts()

def fit_text(c, text, x, y, max_width, font=PDF_FONT, size=8.5):
    text = str(text or "")
    c.setFont(font, size)
    while size > 5 and pdfmetrics.stringWidth(text, font, size) > max_width:
        size -= .25
        c.setFont(font, size)
    c.drawString(x, y, text)

def generate_pdf(d):
    """Draw the form as vector lines/text on one A4 page; no browser print scaling."""
    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    W, H = A4
    L, R = 34, W - 34
    width = R - L

    # Outer frame
    c.setStrokeColor(RULE)
    c.setLineWidth(0.75)
    c.rect(L, 24, width, H - 48, stroke=1, fill=0)

    # Header: bilingual company name and contact block
    c.setFillColor(BLUE)
    c.setFont(PDF_FONT, 15)
    c.drawString(L + 18, H - 57, "NATURAL SHRIMP AQUACULTURE LLC")
    c.setFillColor(INK)
    c.setFont("Times-Bold", 10)
    c.drawString(L + 18, H - 75, "NATURAL SHRIMP AQUACULTURE LLC")
    c.setFillColor(RULE)
    c.setFont(PDF_FONT, 6.4)
    contact = [
        "CR: 1292377, P.O. Box 1459, PC 116, Boushar",
        "Landmark Building, 2nd floor, Muscat, Oman",
        "Tel: +968 22526800, Email: info@oceanic.com",
    ]
    for i, line in enumerate(contact):
        c.drawRightString(R - 12, H - 48 - i*10, line)

    c.setStrokeColor(RULE)
    c.line(L, H - 105, R, H - 105)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W/2, H - 122, "JOB REQUEST")
    c.line(L, H - 132, R, H - 132)

    # Details grid
    top = H - 132
    row_h = 19
    for i in range(4):
        y = top - (i+1)*row_h
        c.line(L, y, R, y)
    split = L + width*0.58
    c.line(split, top, split, top-3*row_h)
    details = [
        ("J.R. NO.", d["J.R. NO."], "DEPT.", d["DEPT."]),
        ("DATE", d["DATE"], "SECTION", d["SECTION"]),
        ("COST CENTER", d["COST CENTER"], "LOCATION / EQUIPMENT", d["LOCATION / EQUIPMENT"]),
    ]
    for i, (a, av, b, bv) in enumerate(details):
        y = top - i*row_h - 13
        fit_text(c, a, L+8, y, 75, size=8)
        fit_text(c, ":", L+89, y, 8, size=8)
        fit_text(c, av, L+101, y, split-(L+108), size=8.5)
        fit_text(c, b, split+8, y, 105, size=8)
        fit_text(c, ":", split+120, y, 6, size=8)
        fit_text(c, bv, split+130, y, R-(split+138), size=8.5)

    # Task description box
    y_task_top = top - 3*row_h
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    c.drawString(L+8, y_task_top-15, "Task Description:")
    task_top = y_task_top - 22
    task_bottom = task_top - 90
    c.line(L, task_top, R, task_top)
    c.line(L, task_bottom, R, task_bottom)
    for i in range(1, 4):
        c.setStrokeColor(colors.HexColor("#C4CCD3"))
        c.line(L, task_top-i*22, R, task_top-i*22)
    c.setFillColor(INK)
    c.setFont(PDF_FONT, 8.5)
    # wrap task description to the available width
    words = str(d["TASK DESCRIPTION"] or "").split()
    lines, current = [], ""
    maxw = width-22
    for word in words:
        test = (current + " " + word).strip()
        if pdfmetrics.stringWidth(test, PDF_FONT, 8.5) > maxw and current:
            lines.append(current); current = word
        else:
            current = test
    if current: lines.append(current)
    for i, line in enumerate(lines[:3]):
        c.drawString(L+12, task_top-15-i*22, line)

    # Approval/sign-off row
    y = task_bottom
    sign_h = 53
    c.line(L, y-sign_h, R, y-sign_h)
    thirds = [L, L+width/3, L+2*width/3, R]
    labels = ["Section", "Department", "Authorized"]
    vals = [d["SECTION FIELD"], d["DEPARTMENT FIELD"], d["AUTHORIZED"]]
    for i in range(3):
        if i:
            c.line(thirds[i], y, thirds[i], y-sign_h)
        c.setFont(PDF_FONT, 8)
        c.setFillColor(INK)
        c.drawCentredString((thirds[i]+thirds[i+1])/2, y-12, labels[i])
        c.setStrokeColor(colors.HexColor("#AEB8C1"))
        c.line(thirds[i]+10, y-39, thirds[i+1]-10, y-39)
        fit_text(c, vals[i], thirds[i]+10, y-34, thirds[i+1]-thirds[i]-20, size=8)

    y -= sign_h
    # Reference / date
    rh = 32
    c.line(L, y-rh, R, y-rh)
    c.setFillColor(INK); c.setFont(PDF_FONT, 8)
    c.drawString(L+8, y-13, "REF. NO.:")
    fit_text(c, d["REF. NO."], L+60, y-13, width*.45, size=8)
    c.drawString(R-105, y-13, "DATE:")
    fit_text(c, d["REF. DATE"], R-68, y-13, 60, size=8)
    c.setStrokeColor(colors.HexColor("#AEB8C1"))
    c.line(L+8, y-25, L+width*.48, y-25)
    c.line(R-115, y-25, R-8, y-25)
    y -= rh

    # Forwarding / checkboxes
    fh = 47
    c.line(L, y-fh, R, y-fh)
    c.setFillColor(INK); c.setFont(PDF_FONT, 8)
    c.drawString(L+8, y-14, "Forwarded to")
    fit_text(c, d["FORWARDED TO"], L+68, y-14, width*.36, size=8)
    c.drawString(L+width*.37, y-32, "For Job to be done")
    c.rect(L+width*.57, y-37, 10, 10, stroke=1, fill=0)
    if d["JOB TO BE DONE"]: c.setFont("Helvetica-Bold", 9); c.drawString(L+width*.57+2, y-35, "x")
    c.drawString(L+width*.66, y-32, "For Inspection")
    c.rect(L+width*.82, y-37, 10, 10, stroke=1, fill=0)
    if d["FOR INSPECTION"]: c.setFont("Helvetica-Bold", 9); c.drawString(L+width*.82+2, y-35, "x")
    c.drawString(L+8, y-43, "Maintenance Engineer:")
    fit_text(c, d["MAINTENANCE ENGINEER"], L+100, y-43, width-110, size=7.5)
    y -= fh

    # Accomplishment report
    def report_section(title, body, height, signature_label=None, signature_value=""):
        nonlocal y
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 8.5)
        c.drawString(L+8, y-13, title)
        c.line(L, y-19, R, y-19)
        content_top = y-19
        content_bottom = y-height
        for k in range(1, max(2, int((height-19)/20))):
            yy = content_top-k*20
            if yy > content_bottom:
                c.setStrokeColor(colors.HexColor("#C4CCD3"))
                c.line(L, yy, R, yy)
        c.setFillColor(INK); c.setFont(PDF_FONT, 7.5)
        body_lines, cur = [], ""
        for word in str(body or "").split():
            test = (cur+" "+word).strip()
            if pdfmetrics.stringWidth(test, PDF_FONT, 7.5) > width-20 and cur:
                body_lines.append(cur); cur=word
            else: cur=test
        if cur: body_lines.append(cur)
        for k, line in enumerate(body_lines[:max(1, int((height-24)/18))]):
            c.drawString(L+10, content_top-13-k*18, line)
        if signature_label:
            c.setFont(PDF_FONT, 7.5)
            c.drawString(L+width*.55, content_bottom+7, signature_label)
            fit_text(c, signature_value, L+width*.72, content_bottom+7, width*.25, size=7)
        y = content_bottom

    report_section("Job Accomplishment Report:", d["ACCOMPLISHMENT REPORT"], 108,
                   "Technical Supervisor:", d["TECHNICAL SUPERVISOR"])
    report_section("Job Requester comment Report:", d["REQUESTER COMMENT"], 82,
                   "Signature:", d["SIGNATURE"])

    # Bottom completion / maintenance engineer fields
    bottom_h = 34
    c.line(L, y-bottom_h, R, y-bottom_h)
    c.setFillColor(INK); c.setFont(PDF_FONT, 8)
    c.drawString(L+8, y-14, "Date of Completion:")
    fit_text(c, d["DATE OF COMPLETION"], L+100, y-14, 95, size=7.5)
    c.drawString(L+width*.52, y-14, "Maintenance Engineer:")
    fit_text(c, d["MAINT. ENG SIGN"], L+width*.76, y-14, width*.22, size=7)
    c.line(L+8, y-25, L+width*.42, y-25)
    c.line(L+width*.52, y-25, R-8, y-25)

    c.showPage()
    c.save()
    out.seek(0)
    return out.getvalue()

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE).fillna("")
        except Exception:
            pass
    return pd.DataFrame(columns=["JR_NO", "DATE", "DEPT", "SECTION", "COST_CENTER", "LOCATION_EQUIP", "TASK_DESC"])

if "next_jr" not in st.session_state:
    hist = load_history()
    nums = pd.to_numeric(hist.get("JR_NO", pd.Series(dtype=str)), errors="coerce").dropna()
    st.session_state.next_jr = int(nums.max()) + 1 if not nums.empty else 3904

# Styled company header
st.markdown("""
<style>
.block-container {max-width: 1150px; padding-top: 1.4rem;}
.company {color:#315F91; text-align:center; font-weight:700; margin:0; line-height:1.2;}
.contact {text-align:right; color:#66717d; font-size:0.78rem; line-height:1.5;}
.form-title {text-align:center; font-size:1.25rem; font-weight:700; border-bottom:2px solid #315F91; padding:0.5rem 0;}
.section-title {color:#263746; font-weight:700; text-decoration:underline;}
</style>
""", unsafe_allow_html=True)
st.markdown('<h2 class="company">الروبيان الطبيعي للاستزراع السمكي ش.م.م</h2>', unsafe_allow_html=True)
st.markdown('<h3 class="company">NATURAL SHRIMP AQUACULTURE LLC</h3>', unsafe_allow_html=True)
st.markdown('<div class="contact">CR: 1292377, P.O. Box 1459, PC 116, Boushar<br>Landmark Building, 2nd floor, Muscat, Oman<br>Tel: +968 22526800, Email: info@oceanic.com</div>', unsafe_allow_html=True)
st.markdown('<div class="form-title">JOB REQUEST</div>', unsafe_allow_html=True)

with st.form("job_request_form"):
    st.markdown("#### Request details")
    a, b = st.columns(2)
    with a:
        jr_no = st.text_input("J.R. NO.", value=str(st.session_state.next_jr), disabled=True)
        req_date = st.date_input("DATE", value=date.today())
        cost_center = st.text_input("COST CENTER", value="22")
    with b:
        dept = st.text_input("DEPT.", value="HATCHERY")
        section = st.text_input("SECTION", value="MECHANICAL")
        location = st.text_input("LOCATION / EQUIPMENT", value="")

    st.markdown("#### Task Description")
    task = st.text_area(" ", value="INSPECT AND FASTEN THE JERKING EXHAUST FAN IN SECTION-E.", height=100)

    st.markdown("#### Routing / authorization")
    s1, s2, s3 = st.columns(3)
    with s1: section_field = st.text_input("Section")
    with s2: department_field = st.text_input("Department")
    with s3: authorized = st.text_input("Authorized")
    r1, r2 = st.columns(2)
    with r1: ref_no = st.text_input("REF. NO.")
    with r2: ref_date = st.date_input("DATE (Ref)", value=date.today())
    forwarded_to = st.text_input("Forwarded to")
    f1, f2 = st.columns(2)
    with f1: job_done = st.checkbox("For Job to be done")
    with f2: inspection = st.checkbox("For Inspection")
    maintenance_engineer = st.text_input("Maintenance Engineer")

    st.markdown("#### Job Accomplishment Report")
    accomplishment = st.text_area("Work done details", height=90)
    supervisor = st.text_input("Technical Supervisor")

    st.markdown("#### Job Requester comment Report")
    requester_comment = st.text_area("Requester comments", height=70)
    c1, c2, c3 = st.columns(3)
    with c1: completion_date = st.date_input("Date of Completion", value=date.today())
    with c2: signature = st.text_input("Signature")
    with c3: maint_sign = st.text_input("Maintenance Engineer (Sign)")

    submitted = st.form_submit_button("Submit Job Request", type="primary", use_container_width=True)

if submitted:
    data = {
        "J.R. NO.": str(jr_no), "DATE": str(req_date), "COST CENTER": cost_center,
        "DEPT.": dept, "SECTION": section, "LOCATION / EQUIPMENT": location,
        "TASK DESCRIPTION": task, "SECTION FIELD": section_field,
        "DEPARTMENT FIELD": department_field, "AUTHORIZED": authorized,
        "REF. NO.": ref_no, "REF. DATE": str(ref_date), "FORWARDED TO": forwarded_to,
        "JOB TO BE DONE": job_done, "FOR INSPECTION": inspection,
        "MAINTENANCE ENGINEER": maintenance_engineer,
        "ACCOMPLISHMENT REPORT": accomplishment, "TECHNICAL SUPERVISOR": supervisor,
        "REQUESTER COMMENT": requester_comment, "DATE OF COMPLETION": str(completion_date),
        "SIGNATURE": signature, "MAINT. ENG SIGN": maint_sign
    }
    hist = load_history()
    row = pd.DataFrame([{
        "JR_NO": str(jr_no), "DATE": str(req_date), "DEPT": dept, "SECTION": section,
        "COST_CENTER": cost_center, "LOCATION_EQUIP": location, "TASK_DESC": task
    }])
    pd.concat([hist, row], ignore_index=True).to_csv(DATA_FILE, index=False)
    pdf_bytes = generate_pdf(data)
    st.session_state.last_pdf = pdf_bytes
    st.session_state.last_pdf_name = f"Job_Request_{jr_no}.pdf"
    st.session_state.next_jr = int(jr_no) + 1
    st.success(f"Job Request #{jr_no} submitted and saved.")
    st.download_button("Download one-page Job Request PDF", data=pdf_bytes,
                       file_name=st.session_state.last_pdf_name, mime="application/pdf",
                       use_container_width=True)

if "last_pdf" in st.session_state and not submitted:
    st.download_button("Download latest Job Request PDF", data=st.session_state.last_pdf,
                       file_name=st.session_state.last_pdf_name, mime="application/pdf",
                       use_container_width=True)

st.divider()
st.subheader("Submitted Job Requests History")
history = load_history()
if history.empty:
    st.info("No job requests submitted yet.")
else:
    st.dataframe(history, use_container_width=True, hide_index=True)

    
    
