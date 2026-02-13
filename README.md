🧠 AI Health Report Analyzer

A Streamlit-based web application that analyzes health parameters and medical report PDFs to generate structured health risk assessments.

🚀 Features

Multi-parameter health risk scoring (BP, glucose, cholesterol, BMI)

Medical report PDF extraction and analysis

Clinical threshold validation

Risk classification (Low / Moderate / High / Critical)

Downloadable health summary report

🛠 Tech Stack

Python

Streamlit

Matplotlib

PyPDF2 / pdfplumber

FPDF

📦 Installation
git clone https://github.com/your-username/ai-health-report-analyzer.git
cd ai-health-report-analyzer
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt


Or install manually:

pip install streamlit matplotlib fpdf PyPDF2 pdfplumber

▶️ Run the App
python -m streamlit run app.py


Open the local URL shown in the terminal (usually http://localhost:8501
).

⚠️ Disclaimer

This tool is for educational purposes only and does not replace professional medical advice.
