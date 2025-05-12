from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

app = FastAPI(title="Polaris Email Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Netlify URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Data Schemas --------
class Project(BaseModel):
    name: str
    description: str
    link: str

class InternshipPreference(BaseModel):
    type: str
    location: str
    duration: str

class Candidate(BaseModel):
    Name: str
    Tags: Optional[str] = ""
    Bio: Optional[str] = ""
    Skills: List[str]
    Badges: List[str]
    CGPA: Optional[float]
    Certifications: List[str]
    Coding_Hours: str
    Projects_Completed: str
    Top_Project: Project
    Looking_For: InternshipPreference
    Email: str
    Phone: str

class EmailPayload(BaseModel):
    recipient_email: str
    subject: str
    candidates: List[Candidate]

# -------- HTML Builder --------
def build_html(candidates: List[Candidate]) -> str:
    rows = ""
    for c in candidates:
        rows += f"""
        <tr>
            <td>{c.Name}</td>
            <td>{c.Tags}</td>
            <td>{c.Bio}</td>
            <td>{", ".join(c.Skills)}</td>
            <td>{", ".join(c.Badges)}</td>
            <td>{c.Coding_Hours}</td>
            <td>{c.Projects_Completed}</td>
            <td><strong>{c.Top_Project.name}</strong><br>{c.Top_Project.description}<br><a href="{c.Top_Project.link}">View</a></td>
            <td>{", ".join(c.Certifications)}</td>
            <td>{c.Looking_For.type} | {c.Looking_For.location} | {c.Looking_For.duration}</td>
            <td>{c.Email}</td>
            <td>{c.Phone}</td>
            <td>{c.CGPA}</td>
        </tr>
        """

    return f"""
    <html><body>
    <h2>Hello Recruiter,</h2>
    <p>Here is the list of shortlisted candidates:</p>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Name</th><th>Tags</th><th>Bio</th><th>Skills</th><th>Badges</th>
            <th>Coding Hours</th><th>Projects Completed</th><th>Top Project</th>
            <th>Certifications</th><th>I'm Looking For</th><th>Email</th><th>Phone</th><th>CGPA</th>
        </tr>
        {rows}
    </table>
    <p>Regards,<br>Polaris Campus Team</p>
    </body></html>
    """

print("🚀 This is the CLEAN version without recipient_name")
# -------- Email Endpoint --------
@app.post("/send_candidate_list_email/")
def send_email(payload: EmailPayload):
    html_body = build_html(payload.candidates)

    email_payload = {
        "orgId": 170,
        "senderId": 1,
        "service": 14,
        "email": {
            "to": [payload.recipient_email],
            "cc": [],
            "from": "pst@ce.classplus.co",
            "templateData": [],
            "subject": payload.subject,
            "content": html_body
        },
        "priority": "P2",
        "uuid": f"polaris-{payload.recipient_email}"
    }

    response = requests.post(
        "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
        json=email_payload,
        headers={
            "Content-Type": "application/json",
            "api_key": os.getenv("CLASSPLUS_EMAIL_API_KEY")
        }
    )

    return {
        "status": "✅ Sent" if response.status_code == 200 else "❌ Failed",
        "response": response.text
    }
