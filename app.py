import streamlit as st

# Page configuration
st.set_page_config(page_title="Natural Shrimp Aquaculture LLC - Job Request", layout="wide")

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
        jr_no = st.text_input("J.R. NO.", value="3904")
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
        st.success(f"Job Request #{jr_no} submitted successfully!")