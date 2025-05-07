from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests

app = FastAPI()

# ✅ CORS: allow frontend from Netlify to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["https://chic-klepon-77ad14.netlify.app"] for strict mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Hardcoded API key (replace with env later)
API_KEY = "N6FPaqWC658jH0d7u7Qoh7xTugP5Mw_IJQGjbnQXkUmDL-9hCaVFQg"

# === MODELS ===
class Project(BaseModel):
    name: str
    description: str
    link: Optional[str] = ""

class LookingFor(BaseModel):
    type: str
    location: str
    duration: str

class Candidate(BaseModel):
    Name: str
    Tags: Optional[List[str]] = []
    Bio: str
    Skills: List[str]
    Badges: Optional[List[str]] = []
    CGPA: Optional[float]
    Certifications: Optional[List[str]] = []
    Coding_Hours: Optional[int]
    Projects_Completed: Optional[int]
    Top_Project: Optional[Project]
    Looking_For: Optional[LookingFor]
    Email: Optional[str]
    Phone: Optional[str]

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

# === EMAIL API ===
@app.post("/send_candidate_list_email/")
def send_candidate_list_email(payload: EmailRequest):
    try:
        html_content = generate_html(payload)

        data = {
            "to": [payload.recipient_email],
            "subject": payload.subject,
            "body": html_content
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }

        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=data,
            headers=headers
        )

        print("📤 Status Code:", response.status_code)
        print("📤 Response:", response.text)

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        print("❌ Exception:", str(e))
        return {
            "status": "❌ Exception",
            "details": str(e)
        }

# === HTML BUILDER ===
def generate_html(payload: EmailRequest):
    rows = ""
    for c in payload.candidates:
        tags = ", ".join(c.Tags) if c.Tags else ""
        skills = ", ".join(c.Skills)
        badges = ", ".join(c.Badges) if c.Badges else ""
        certs = ", ".join(c.Certifications) if c.Certifications else ""
        project = f"<strong>{c.Top_Project.name}</strong>: {c.Top_Project.description} <a href='{c.Top_Project.link}'>View</a>" if c.Top_Project else ""
        looking = f"{c.Looking_For.location} | {c.Looking_For.type} | {c.Looking_For.duration}" if c.Looking_For else ""

        rows += f"""
        <tr>
            <td>{c.Name}</td>
            <td>{tags}</td>
            <td>{c.Bio}</td>
            <td>{skills}</td>
            <td>{badges}</td>
            <td>{c.Coding_Hours}</td>
            <td>{c.Projects_Completed}</td>
            <td>{project}</td>
            <td>{certs}</td>
            <td>{looking}</td>
            <td>{c.Email}</td>
            <td>{c.Phone}</td>
            <td>{c.CGPA if c.CGPA else ''}</td>
        </tr>
        """

    return f"""
    <html>
    <body>
        <h3>Hello Recruiter,</h3>
        <p>Here is the list of shortlisted candidates:</p>
        <table border="1" cellspacing="0" cellpadding="6">
            <tr>
                <th>Name</th>
                <th>Tags</th>
                <th>Bio</th>
                <th>Skills</th>
                <th>Badges</th>
                <th>Coding Hours</th>
                <th>Projects Completed</th>
                <th>Top Project</th>
                <th>Certifications</th>
                <th>Looking For</th>
                <th>Email</th>
                <th>Phone</th>
                <th>CGPA</th>
            </tr>
            {rows}
        </table>
        <br />
        <p>– Polaris Campus Team</p>
    </body>
    </html>
    """
