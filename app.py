import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from pypdf import PdfReader

# --------------------------
# INITIAL SETUP
# --------------------------

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found in .env file")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Advanced AI Health Dashboard", page_icon="🏥", layout="wide")

st.title("🏥 Advanced AI Health Intelligence System")
st.warning("⚠️ This tool does NOT replace professional medical advice.")

# --------------------------
# SESSION STATE
# --------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ai_report" not in st.session_state:
    st.session_state.ai_report = ""

# --------------------------
# USER INPUT
# --------------------------

col1, col2 = st.columns(2)

with col1:
    age = st.slider("Age", 1, 100, 30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", 100, 250, 170)
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    waist = st.number_input("Waist Circumference (cm)", 50, 150, 85)

with col2:
    systolic = st.number_input("Systolic BP (mmHg)", 80, 220, 120)
    diastolic = st.number_input("Diastolic BP (mmHg)", 40, 140, 80)
    resting_hr = st.number_input("Resting Heart Rate (bpm)", 40, 160, 70)
    fasting_glucose = st.number_input("Fasting Glucose (mg/dL)", 60, 350, 90)
    cholesterol = st.number_input("Total Cholesterol (mg/dL)", 100, 400, 180)

exercise = st.selectbox("Exercise Frequency", ["None", "1-2/week", "3-5/week", "Daily"])
sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])
stress = st.selectbox("Stress Level", ["Low", "Moderate", "High"])
smoking = st.selectbox("Smoking", ["No", "Occasional", "Yes"])
alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Regular"])

symptoms = st.multiselect(
    "Select Symptoms",
    ["Headache", "Fever", "Cough", "Fatigue",
     "Chest pain", "Shortness of breath",
     "Dizziness", "Joint pain", "None"]
)

# --------------------------
# CLINICAL FUNCTIONS
# --------------------------

bmi = weight / ((height / 100) ** 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", 15
    elif bmi < 25:
        return "Normal", 0
    elif bmi < 30:
        return "Overweight", 10
    else:
        return "Obese", 20

def blood_pressure_risk(sys, dia):
    if sys >= 180 or dia >= 120:
        st.error("🚨 Hypertensive Crisis. Seek emergency care.")
        st.stop()
    if sys >= 140 or dia >= 90:
        return 20
    elif sys >= 130 or dia >= 85:
        return 10
    return 0

def glucose_risk(glucose):
    if glucose >= 250:
        st.error("🚨 Critically high glucose level detected.")
        st.stop()
    if glucose >= 126:
        return 20
    elif glucose >= 100:
        return 10
    return 0

def cholesterol_risk(chol):
    if chol >= 240:
        return 20
    elif chol >= 200:
        return 10
    return 0

def heart_rate_risk(hr):
    if hr >= 140:
        st.error("🚨 Abnormally high resting heart rate.")
        st.stop()
    if hr > 100:
        return 10
    return 0

def waist_risk(waist, gender):
    if gender == "Male" and waist > 102:
        return 15
    if gender == "Female" and waist > 88:
        return 15
    return 0

def age_risk(age):
    if age >= 60:
        return 15
    elif age >= 45:
        return 8
    return 0

def classify_health(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Moderate Risk"
    elif score >= 40:
        return "High Risk"
    else:
        return "Critical Risk"

# --------------------------
# RISK CALCULATION
# --------------------------

category, bmi_risk = bmi_category(bmi)

risk_factors = {
    "BMI Risk": bmi_risk,
    "Waist Risk": waist_risk(waist, gender),
    "Blood Pressure": blood_pressure_risk(systolic, diastolic),
    "Glucose": glucose_risk(fasting_glucose),
    "Cholesterol": cholesterol_risk(cholesterol),
    "Heart Rate": heart_rate_risk(resting_hr),
    "Age Risk": age_risk(age),
    "No Exercise": 15 if exercise == "None" else 0,
    "Poor Sleep": 15 if sleep == "Poor" else 0,
    "High Stress": 15 if stress == "High" else 0,
    "Smoking": 20 if smoking == "Yes" else 0,
    "Alcohol": 10 if alcohol == "Regular" else 0
}

symptom_penalty = len(symptoms) * 5 if "None" not in symptoms else 0
risk_factors["Symptoms"] = min(symptom_penalty, 20)

health_score = max(0, 100 - sum(risk_factors.values()))
health_class = classify_health(health_score)

# --------------------------
# METABOLIC SYNDROME CHECK
# --------------------------

metabolic_flags = 0
if bmi >= 30: metabolic_flags += 1
if waist_risk(waist, gender) > 0: metabolic_flags += 1
if fasting_glucose >= 100: metabolic_flags += 1
if systolic >= 130 or diastolic >= 85: metabolic_flags += 1
if cholesterol >= 200: metabolic_flags += 1

if metabolic_flags >= 3:
    st.error("⚠️ Possible Metabolic Syndrome Risk Detected.")

# --------------------------
# DASHBOARD
# --------------------------

st.subheader("📊 Health Overview")

col3, col4 = st.columns(2)

with col3:
    st.metric("BMI", round(bmi, 2))
    st.metric("BMI Category", category)
    st.metric("Health Score", f"{health_score}/100")
    st.metric("Overall Status", health_class)

with col4:
    fig, ax = plt.subplots()
    ax.barh(list(risk_factors.keys()), list(risk_factors.values()))
    ax.set_title("Risk Contribution")
    ax.set_xlabel("Risk Points")
    st.pyplot(fig)

# --------------------------
# AI REPORT GENERATION
# --------------------------

if st.button("Generate AI Report"):

    critical_symptoms = {"Chest pain", "Shortness of breath", "Dizziness"}

    if any(s in critical_symptoms for s in symptoms):
        st.error("🚨 Emergency symptoms detected. Seek medical attention immediately.")
    else:
        with st.spinner("Generating AI Report..."):

            prompt = f"""
Perform structured preventive health analysis.

Age: {age}
Gender: {gender}
BMI: {round(bmi,2)} ({category})
Waist: {waist}
Blood Pressure: {systolic}/{diastolic}
Heart Rate: {resting_hr}
Fasting Glucose: {fasting_glucose}
Cholesterol: {cholesterol}
Health Score: {health_score}
Symptoms: {symptoms}

Include:
1. Cardiometabolic risk
2. Lifestyle risk
3. Long-term disease probability
4. Improvement protocol
5. Red flag review
6. Disclaimer
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a structured clinical health assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            st.session_state.ai_report = response.choices[0].message.content
            st.success("Report Generated")

if st.session_state.ai_report:
    st.markdown(st.session_state.ai_report)

# --------------------------
# PDF EXPORT
# --------------------------

if st.session_state.ai_report:

    if st.button("Download PDF Report"):

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        pdf.cell(200, 10, txt="AI Health Report", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Date: {datetime.now()}", ln=True)
        pdf.multi_cell(0, 8, txt=st.session_state.ai_report)

        filename = "health_report.pdf"
        pdf.output(filename)

        with open(filename, "rb") as f:
            st.download_button("📄 Download PDF", f, "AI_Health_Report.pdf")

# --------------------------
# CHATBOT
# --------------------------

st.divider()
st.subheader("💬 AI Health Chatbot")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask about your health...")

if user_input:

    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Provide safe health guidance without diagnosis."},
            *st.session_state.chat_history[-10:]
        ],
        temperature=0.5
    )

    reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)

# --------------------------
# PDF HEALTH REPORT ANALYZER
# --------------------------

st.divider()
st.subheader("📂 Analyze External Health Report PDF")

uploaded_file = st.file_uploader("Upload a medical report PDF", type=["pdf"])

if uploaded_file is not None:

    try:
        reader = PdfReader(uploaded_file)
        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            st.error("Could not extract readable text.")
        else:
            st.success("PDF text extracted successfully.")

            if st.button("Analyze Uploaded Report"):

                with st.spinner("Analyzing medical report..."):

                    extracted_text = extracted_text[:8000]

                    pdf_prompt = f"""
Analyze this medical report.

1. Identify abnormal values
2. Cardiovascular risk
3. Metabolic risk
4. Red flags
5. Preventive advice
6. When to consult doctor
7. Disclaimer

Report Content:
{extracted_text}
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a clinical medical report analyst."},
                            {"role": "user", "content": pdf_prompt}
                        ],
                        temperature=0.3
                    )

                    pdf_analysis = response.choices[0].message.content

                    st.subheader("📋 AI Analysis of Uploaded Report")
                    st.markdown(pdf_analysis)

    except Exception as e:
        st.error(f"Error processing PDF: {e}")
