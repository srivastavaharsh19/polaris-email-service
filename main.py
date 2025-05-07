from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests

app = FastAPI()

# Allow CORS for Bolt frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEMP: Hardcoded API key for debugging
API_KEY = "N6FpaqWC658jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg"  # ⚠️ Remove this later

# ---------- Models ----------
class TopProject(BaseModel):
    name: str
    description: str
    link: Optional[str] = ""

class InternshipPreference(BaseModel):
    type: str
    location: str
    duration: str

class Candidate(BaseModel):
    Name: str
    Tags: str
    Bio: str
    Skills: List[str]
    Badges: List[str]
    CGPA: Optional[float]
    Certifications: List[str]
    Coding_Hours: str
    Projects_Completed: str
    Top_Project: TopProject
    Looking_For: InternshipPreference
    Email: str
    Phone: str

class CandidateEmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

# ---------- Email Formatter ----------
def build_html_email(candidates: List[Candidate]) -> str:
    rows = ""
    for c in candidates:
        rows += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ccc;"><strong>{c.Name}</strong><br>
                <small>{c.Tags}</small><br><br>
                <strong>Skills:</strong> {', '.join(c.Skills)}<br>
                <strong>CGPA:</strong> {c.CGPA or '—'}<br>
                <strong>Badges:</strong> {', '.join(c.Badges)}<br>
                <strong>Certifications:</strong> {', '.join(c.Certifications)}<br><br>
                <strong>Top Project:</strong> {c.Top_Project.name}<br>
                {c.Top_Project.description}<br>
                <a href="{c.Top_Project.link}" target="_blank">{c.Top_Project.link}</a><br><br>
                <strong>Internship Pref:</strong> {c.Looking_For.type}, {c.Looking_For.location}, {c.Looking_For.duration}<br>
                <strong>Email:</strong> {c.Email}<br>
                <strong>Phone:</strong> {c.Phone}
            </td>
        </tr>
        """

    return f"""
    <html>
    <body>
        <h2>Your Shortlisted Polaris Candidates</h2>
        <table style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif;">
            {rows}
        </table>
        <br>
        <p style="font-size: 12px; color: #888;">Sent via Polaris School of Technology</p>
    </body>
    </html>
    """

# ---------- Email Sending Endpoint ----------
@app.post("/send_candidate_list_email/")
async def send_email(payload: CandidateEmailRequest):
    html_body = build_html_email(payload.candidates)

    email_payload = {
        "to": [payload.recipient_email],
        "subject": payload.subject,
        "body": html_body,
        "bodyType": "html",
        "sender": {
            "email": "connect@emails.testbook.com",
            "name": "Polaris Campus"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "api_key": API_KEY  # hardcoded for now
    }

    try:
        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=email_payload,
            headers=headers
        )

        print("📤 Status Code:", response.status_code)
        print("📩 Response Text:", response.text)

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed",
            "details": response.text
        }

    except Exception as e:
        print("❌ Exception:", str(e))
        return {
            "status": "❌ Exception",
            "details": str(e)
        }
