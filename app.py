import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# Page configuration
st.set_page_config(page_title="Natural Shrimp Aquaculture LLC - Job Request", layout="wide")

# File to store history
DATA_FILE = "job_requests_history.csv"

# Load existing data or create empty DataFrame
if os.path.exists(DATA_FILE):
    df_history = pd.read_csv(DATA_FILE)
else:
    df_history = pd.DataFrame(columns=["JR_NO", "DATE", "DEPT", "SECTION", "COST_CENTER", "LOCATION_EQUIP", "TASK_DESC"])

# Auto-increment JR NO starting from 3904
if not df_history.empty and "JR_NO" in df_history.columns:
    try:
        last_jr = int(df_history["JR_NO"].iloc[-1])
        next_jr = last_jr + 1
    except:
        next_jr = 3904
else:
    next_jr = 3904

# Function to generate PDF
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, "NATURAL SHRIMP AQUACULTURE LLC", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "JOB REQUEST FORM", ln=True, align='C')
    pdf.ln(5)
    
    # Form details
    pdf.set_font("Arial", size=11)
    for key, value in data.items():
        pdf.cell(0, 8, f"{key}: {value}", ln=True)
    
    pdf_file = f"Job_Request_{data['J.R. NO.']}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Header Section (Company Branding)
st.markdown("<h2 style='text-align: center; color: #004d99;'>الروبيان الطبيعي للاستزراع السمكي ش.م.م</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #004d99;'>NATURAL SHRIMP AQUACULTURE LLC</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; border-bottom: 2px solid #004d99; padding-bottom: 10px;'>JOB REQUEST</h4>", unsafe_allow_html=True)

# Contact info subtext
st.markdown(
    "<p style='text-align: right; font-size: 12px; color: gray;'>"
    "ص.ب: 1409، ر.م: 116، بوشر، مبنى لاندمارك، الطابق الثاني، مسقط، سلطنة عمان<br>"
    "CR: 1292377, P.O. Box 1459, PC 116, Boushar, Landmark Building, 2nd floor, Muscat, Oman<br>"
    "Tel: +968 22526800, Email: info@oceanic.com"
    "</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# Form inputs layout
with st.form("job_request_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        jr_no = st.text_input("J.R. NO.", value=str(next_jr), disabled=True)
        date = st.date_input("DATE")
        cost_center = st.text_input("COST CENTER", value="22")
        
    with col2:
        dept = st.text_input("DEPT.", value="HATCHERY")
        section = st.text_input("SECTION", value="MECHANICAL")
        location_equip = st.text_input("LOCATION / EQUIPMENT")

    st.markdown("---")
    
    # Task Description
    st.markdown("#### **Task Description:**")
    task_description = st.text_area("Describe the task here...", value="INSPECT AND FASTEN THE JERKING EXHAUST FAN IN SECTION-E.")

    st.markdown("---")

    # Sign-off metadata row
    col3, col4, col5 = st.columns(3)
    with col3:
        sec_field = st.text_input("Section")
    with col4:
        dept_field = st.text_input("Department")
    with col5:
        authorized = st.text_input("Authorized")

    col6, col7 = st.columns(2)
    with col6:
        ref_no = st.text_input("REF. NO.")
    with col7:
        ref_date = st.date_input("DATE (Ref)")

    st.markdown("---")

    # Forward options
    st.markdown("#### **Forwarding Options:**")
    forwarded_to = st.text_input("Forwarded to")
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        job_to_be_done = st.checkbox("For Job to be done")
    with f_col2:
        for_inspection = st.checkbox("For Inspection")
        
    maintenance_engineer = st.text_input("Maintenance Engineer")

    st.markdown("---")

    # Job Accomplishment Report Section
    st.markdown("#### **Job Accomplishment Report:**")
    accomplishment_report = st.text_area("Enter work done details...")
    technical_supervisor = st.text_input("Technical Supervisor")

    st.markdown("---")

    # Job Requester comment Report Section
    st.markdown("#### **Job Requester comment Report:**")
    requester_comment = st.text_area("Enter requester comments...")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        date_of_completion = st.date_input("Date of Completion")
    with c_col2:
        signature = st.text_input("Signature")
    with c_col3:
        maint_engineer_sign = st.text_input("Maintenance Engineer (Sign)")

    st.markdown("---")
    
    # Submit button
    submitted = st.form_submit_button("Submit Job Request")

if submitted:
    # Prepare record data
    new_data = {
        "J.R. NO.": jr_no,
        "DATE": str(date),
        "COST CENTER": cost_center,
        "DEPT.": dept,
        "SECTION": section,
        "LOCATION / EQUIPMENT": location_equip,
        "TASK DESCRIPTION": task_description,
        "SECTION FIELD": sec_field,
        "DEPARTMENT FIELD": dept_field,
        "AUTHORIZED": authorized,
        "REF. NO.": ref_no,
        "REF. DATE": str(ref_date),
        "FORWARDED TO": forwarded_to,
        "JOB TO BE DONE": job_to_be_done,
        "FOR INSPECTION": for_inspection,
        "MAINTENANCE ENGINEER": maintenance_engineer,
        "ACCOMPLISHMENT REPORT": accomplishment_report,
        "TECHNICAL SUPERVISOR": technical_supervisor,
        "REQUESTER COMMENT": requester_comment,
        "DATE OF COMPLETION": str(date_of_completion),
        "SIGNATURE": signature,
        "MAINT. ENG SIGN": maint_engineer_sign
    }
    
    # Save to CSV history
    new_row = pd.DataFrame([{
        "JR_NO": jr_no,
        "DATE": str(date),
        "DEPT": dept,
        "SECTION": section,
        "COST_CENTER": cost_center,
        "LOCATION_EQUIP": location_equip,
        "TASK_DESC": task_description
    }])
    
    df_updated = pd.concat([df_history, new_row], ignore_index=True)
    df_updated.to_csv(DATA_FILE, index=False)
    
    st.success(f"Job Request #{jr_no} submitted and saved successfully!")
    
    # Generate PDF
    pdf_filename = generate_pdf(new_data)
    
    with open(pdf_filename, "rb") as file:
        st.download_button(
            label="📄 Download Job Request PDF",
            data=file,
            file_name=pdf_filename,
            mime="application/pdf"
        )

# Display History Section
st.markdown("---")
st.markdown("### **📋 Submitted Job Requests History**")
if os.path.exists(DATA_FILE):
    history_df = pd.read_csv(DATA_FILE)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No job requests submitted yet.")
