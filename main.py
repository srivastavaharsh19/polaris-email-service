from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# CORS config (adjust domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Project(BaseModel):
    name: str
    description: str
    link: str

class LookingFor(BaseModel):
    type: str
    location: str
    duration: str

class Candidate(BaseModel):
    Name: str
    Tags: Optional[str]
    Bio: Optional[str]
    Skills: List[str]
    Badges: Optional[List[str]]
    Coding_Hours: Optional[int]
    Projects_Completed: Optional[int]
    Top_Project: Optional[Project]
    Certifications: Optional[List[str]]
    Looking_For: Optional[LookingFor]
    Email: Optional[str]
    Phone: Optional[str]
    CGPA: Optional[float]

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_candidate_list_email(payload: EmailRequest, request: Request):
    print("✅ Received payload:", payload.dict())

    # Email table content
    rows = ""
    for c in payload.candidates:
        top_proj_html = (
            f"<b>{c.Top_Project.name}</b><br>{c.Top_Project.description}<br><a href='{c.Top_Project.link}'>View Project</a>"
            if c.Top_Project else "—"
        )
        certs = "<br>".join(c.Certifications) if c.Certifications else "—"
        looking = f"{c.Looking_For.location} | {c.Looking_For.type} | {c.Looking_For.duration}" if c.Looking_For else "—"
        badges = ", ".join(c.Badges) if c.Badges else "—"
        skills = ", ".join(c.Skills) if c.Skills else "—"

        rows += f"""
        <tr>
            <td>{c.Name}</td>
            <td>{c.Tags or "—"}</td>
            <td>{c.Bio or "—"}</td>
            <td>{skills}</td>
            <td>{badges}</td>
            <td>{c.Coding_Hours or "—"}</td>
            <td>{c.Projects_Completed or "—"}</td>
            <td>{top_proj_html}</td>
            <td>{certs}</td>
            <td>{looking}</td>
            <td>{c.Email or "—"}</td>
            <td>{c.Phone or "—"}</td>
            <td>{c.CGPA or "—"}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <body>
        <p><b>Hello {payload.recipient_name},</b></p>
        <p>Here is the list of shortlisted candidates for your review:</p>
        <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; font-family: Arial; font-size: 14px;">
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
                <th>I'm Looking For</th>
                <th>Email</th>
                <th>Phone</th>
                <th>CGPA</th>
            </tr>
            {rows}
        </table>
        <br><p>Best regards,<br><b>Polaris Campus Team</b></p>
    </body>
    </html>
    """

    # Send email using internal Classplus API
    data = {
        "to": [payload.recipient_email],
        "subject": payload.subject,
        "message": html_content
    }

    headers = {
        "Content-Type": "application/json",
        "api_key": os.environ.get("CLASSPLUS_EMAIL_API_KEY")
    }

    try:
        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=data,
            headers=headers
        )
        print("📬 Status Code:", response.status_code)
        print("📬 Response:", response.text)

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
