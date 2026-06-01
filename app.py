import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import requests
st.title("Health Prediction Application")
st.markdown(
    """
    This application predicts possible health risks using patient blood test values,
    CRUD operations, and healthcare API integration.
    """
)

def get_health_info():

    url = "https://api.fda.gov/drug/event.json?limit=1"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        return "FDA healthcare data fetched successfully."

    else:

        return "Unable to fetch FDA data."

st.sidebar.title("MIRA Health System")
st.sidebar.write("AI-powered Healthcare Prediction App")

# Database Connection
conn = sqlite3.connect("health_data.db")
cursor = conn.cursor()

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    dob TEXT,
    email TEXT,
    glucose REAL,
    haemoglobin REAL,
    cholesterol REAL,
    remarks TEXT
)
""")

conn.commit()



# User Inputs
col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    glucose = st.number_input("Glucose", min_value=0.0)

with col2:
    dob = st.date_input("Date of Birth")
    haemoglobin = st.number_input("Haemoglobin", min_value=0.0)
    cholesterol = st.number_input("Cholesterol", min_value=0.0)

# Prediction Logic
api_result = get_health_info()
remarks = ""

if glucose > 140:
    remarks += "Possible diabetes risk. "

if cholesterol > 240:
    remarks += "High cholesterol risk. "

if haemoglobin < 12:
    remarks += "Low haemoglobin level. "

if remarks == "":
    remarks = "Normal health indicators."

# Save Button
if st.button("Predict & Save"):

    # Validation Checks
    if full_name == "":
        st.error("Full Name is required.")

    elif "@" not in email or "." not in email:
        st.error("Enter a valid email address.")

    elif dob > date.today():
        st.error("Date of Birth cannot be a future date.")

    else:

        cursor.execute("""
        INSERT INTO patients
        (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, str(dob), email, glucose, haemoglobin, cholesterol, remarks))

        conn.commit()

        st.success("Patient data saved successfully!")
        st.success(f"Predicted Health Remark: {remarks}")
        st.write(api_result)

# Display Records
st.subheader("Patient Records")
st.write("---")
search_name = st.text_input("Search Patient by Name")

if search_name:

    query = f"""
    SELECT * FROM patients
    WHERE full_name LIKE '%{search_name}%'
    """

    df = pd.read_sql_query(query, conn)

else:

    df = pd.read_sql_query("SELECT * FROM patients", conn)
st.metric("Total Patients", len(df))

st.dataframe(df)
st.subheader("Delete Record")

delete_id = st.number_input("Enter Patient ID to Delete", step=1)

if st.button("Delete Record"):

    cursor.execute("DELETE FROM patients WHERE id = ?", (delete_id,))

    conn.commit()

    st.warning("Record deleted successfully!")

st.subheader("Update Patient Record")

update_id = st.number_input("Enter Patient ID to Update", step=1, key="update")

if st.button("Load Record"):

    cursor.execute("SELECT * FROM patients WHERE id = ?", (update_id,))
    record = cursor.fetchone()

    if record:

        st.session_state["update_data"] = record

    else:
        st.error("Record not found.")

if "update_data" in st.session_state:

    record = st.session_state["update_data"]

    updated_name = st.text_input("Update Full Name", value=record[1])

    updated_email = st.text_input("Update Email", value=record[3])

    updated_glucose = st.number_input("Update Glucose", value=float(record[4]))

    updated_haemoglobin = st.number_input("Update Haemoglobin", value=float(record[5]))

    updated_cholesterol = st.number_input("Update Cholesterol", value=float(record[6]))
    updated_remarks = ""

    if updated_glucose > 140:
        updated_remarks += "Possible diabetes risk. "

    if updated_cholesterol > 240:
        updated_remarks += "High cholesterol risk. "

    if updated_haemoglobin < 12:
        updated_remarks += "Low haemoglobin level. "

    if updated_remarks == "":
        updated_remarks = "Normal health indicators."

    if st.button("Update Record"):

        cursor.execute("""
        UPDATE patients
        SET full_name = ?,
            email = ?,
            glucose = ?,
            haemoglobin = ?,
            cholesterol = ?,
            remarks = ?
        WHERE id = ?
        """, (
            updated_name,
            updated_email,
            updated_glucose,
            updated_haemoglobin,
            updated_cholesterol,
            updated_remarks,
            update_id
        ))

        conn.commit()

        st.success("Record updated successfully!")

st.write("---")
st.caption("Developed by Afreen | Junior AI/ML Developer Assignment")