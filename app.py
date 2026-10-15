
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from streamlit_gsheets import GSheetsConnection

# -----------------------------
# APP SETTINGS
# -----------------------------
st.set_page_config(
    page_title="Natural Shrimp Job Request",
    page_icon="📋",
    layout="wide",
)

SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1osWAalmjJn3ZdGuqY5i_6R1IVK0CyPB46riHyKeWGys/edit"
)
WORKSHEET = "JobHistory"
STARTING_JR_NO = 3904

HISTORY_COLUMNS = [
    "JR_NO",
    "DATE",
    "DEPT",
    "SECTION",
    "COST_CENTER",
    "LOCATION_EQUIP",
    "TASK_DESC",
    "Status",
]

# -----------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)


def load_history():
    conn = get_connection()

    df = conn.read(
        spreadsheet=SPREADSHEET_URL,
        worksheet=WORKSHEET,
        ttl=0,
    )

    if df is None or df.empty:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    df = df.fillna("")

    for col in HISTORY_COLUMNS:
        if col not in df.columns:
            df[col] = "Pending" if col == "Status" else ""

    df = df[HISTORY_COLUMNS].copy()
    df["JR_NO"] = df["JR_NO"].astype(str)

    return df


def save_history(df):
    clean_df = df.copy()

    for col in HISTORY_COLUMNS:
        if col not in clean_df.columns:
            clean_df[col] = "Pending" if col == "Status" else ""

    clean_df = clean_df[HISTORY_COLUMNS].fillna("")

    get_connection().update(
        spreadsheet=SPREADSHEET_URL,
        worksheet=WORKSHEET,
        data=clean_df,
    )


def get_next_jr_number(history):
    if history.empty:
        return STARTING_JR_NO

    numbers = pd.to_numeric(
        history["JR_NO"], errors="coerce"
    ).dropna()

    if numbers.empty:
        return STARTING_JR_NO

    return max(STARTING_JR_NO, int(numbers.max()) + 1)


# -----------------------------
# PDF GENERATION
# -----------------------------
def create_pdf(request_data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 60

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "NATURAL SHRIMP")
    y -= 28

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "JOB REQUEST")
    y -= 35

    pdf.setFont("Helvetica", 10)

    fields = [
        ("J.R. NO.", request_data["JR_NO"]),
        ("DATE", request_data["DATE"]),
        ("DEPARTMENT", request_data["DEPT"]),
        ("SECTION", request_data["SECTION"]),
        ("COST CENTER", request_data["COST_CENTER"]),
        ("LOCATION / EQUIPMENT", request_data["LOCATION_EQUIP"]),
        ("STATUS", request_data["Status"]),
    ]

    for label, value in fields:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(210, y, str(value)[:90])
        y -= 23

    y -= 8
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "TASK DESCRIPTION:")
    y -= 20

    pdf.setFont("Helvetica", 10)
    description = str(request_data["TASK_DESC"])

    # Wrap the task description into printable lines.
    words = description.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()

        if pdf.stringWidth(test_line, "Helvetica", 10) > width - 100:
            pdf.drawString(50, y, line)
            y -= 16
            line = word

            if y < 80:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 60
        else:
            line = test_line

    if line:
        pdf.drawString(50, y, line)

    y -= 50
    if y < 70:
        pdf.showPage()
        y = height - 60

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, "Prepared by: ____________________")
    pdf.drawString(330, y, "Approved by: ____________________")

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()


# -----------------------------
# LOAD HISTORY AND JR NUMBER
# -----------------------------
st.title("Natural Shrimp - Job Request")

try:
    history = load_history()
except Exception as exc:
    st.error(
        "Could not connect to Google Sheets. "
        "Check Streamlit Secrets, sheet sharing, and the "
        "JobHistory worksheet."
    )
    st.code(str(exc))
    st.stop()

# Always derive the number from the saved history.
next_jr = get_next_jr_number(history)

# -----------------------------
# NEW JOB REQUEST FORM
# -----------------------------
st.subheader("Create Job Request")

with st.form("job_request_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        jr_no = st.text_input(
            "J.R. NO.",
            value=str(next_jr),
            disabled=True,
        )

        request_date = st.date_input(
            "Date",
            value=date.today(),
        )

        department = st.text_input("Department")
        section = st.text_input("Section")

    with col2:
        cost_center = st.text_input("Cost Center")
        location_equip = st.text_input("Location / Equipment")

        status = st.selectbox(
            "Status",
            ["Pending", "In Progress", "Completed"],
        )

    task_desc = st.text_area(
        "Task Description",
        height=150,
    )

    submitted = st.form_submit_button(
        "Save Job Request",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not department.strip():
        st.error("Please enter the Department.")
    elif not task_desc.strip():
        st.error("Please enter the Task Description.")
    else:
        try:
            # Re-read the latest history before saving.
            latest_history = load_history()
            new_jr = get_next_jr_number(latest_history)

            new_row = pd.DataFrame(
                [
                    {
                        "JR_NO": str(new_jr),
                        "DATE": request_date.isoformat(),
                        "DEPT": department.strip(),
                        "SECTION": section.strip(),
                        "COST_CENTER": cost_center.strip(),
                        "LOCATION_EQUIP": location_equip.strip(),
                        "TASK_DESC": task_desc.strip(),
                        "Status": status,
                    }
                ],
                columns=HISTORY_COLUMNS,
            )

            updated_history = pd.concat(
                [latest_history, new_row],
                ignore_index=True,
            )

            save_history(updated_history)

            st.success(
                f"Job Request JR-{new_jr} saved to Google Sheets."
            )

            st.download_button(
                label="Download Job Request PDF",
                data=create_pdf(new_row.iloc[0].to_dict()),
                file_name=f"JR_{new_jr}.pdf",
                mime="application/pdf",
            )

        except Exception as exc:
            st.error("Could not save the Job Request.")
            st.code(str(exc))

# -----------------------------
# JOB REQUEST HISTORY
# -----------------------------
st.divider()
st.subheader("Job Request History")

try:
    history = load_history()

    if history.empty:
        st.info("No Job Requests have been saved yet.")
    else:
        display_history = history.copy()

        search = st.text_input(
            "Search by JR number, department, or task"
        )

        if search.strip():
            mask = display_history.astype(str).apply(
                lambda column: column.str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)

            display_history = display_history[mask]

        st.dataframe(
            display_history,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"{len(display_history)} request(s) displayed."
        )

        # Select a request to update its status.
        st.subheader("Update Request Status")

        jr_options = history["JR_NO"].astype(str).tolist()

        selected_jr = st.selectbox(
            "Select JR number",
            options=jr_options,
        )

        current_row = history[
            history["JR_NO"].astype(str) == selected_jr
        ].iloc[0]

        status_options = [
            "Pending",
            "In Progress",
            "Completed",
        ]

        current_status = str(current_row["Status"])
        if current_status not in status_options:
            status_options.append(current_status)

        new_status = st.selectbox(
            "New status",
            options=status_options,
            index=status_options.index(current_status),
        )

        if st.button("Update Status"):
            try:
                history.loc[
                    history["JR_NO"].astype(str) == selected_jr,
                    "Status",
                ] = new_status

                save_history(history)

                st.success(
                    f"JR-{selected_jr} status updated to {new_status}."
                )
                st.rerun()

            except Exception as exc:
                st.error("Could not update the status.")
                st.code(str(exc))

        # Download a PDF for an existing request.
        st.subheader("Download Existing Request")

        pdf_jr = st.selectbox(
            "Choose JR number for PDF",
            options=jr_options,
            key="pdf_jr",
        )

        pdf_row = history[
            history["JR_NO"].astype(str) == pdf_jr
        ].iloc[0]

        st.download_button(
            label="Download Selected Request PDF",
            data=create_pdf(pdf_row.to_dict()),
            file_name=f"JR_{pdf_jr}.pdf",
            mime="application/pdf",
        )

except Exception as exc:
    st.error("Could not display or update the history.")
    st.code(str(exc))
