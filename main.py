from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

# ✅ FastAPI instance with docs enabled
app = FastAPI(
    title="Polaris Email Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ CORS Middleware (allows Bolt + Postman to work)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your Bolt domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATA SCHEMA --------------------

class Project(BaseModel):
    name: str
    description: str
    link: str

class InternshipPreference(BaseModel):
    type: str
    location: str
    duration: str

class Candidate(BaseModel):
    name: str
    tags: Optional[str] = ""
    bio: Optional[str] = ""
    skills: List[str]
    badges: List[str]
    cgpa: Optional[float]
    certifications: List[str]
    coding_hours: str
    projects_completed: str
    top_project: Project
    looking_for: InternshipPreference
    email: str
    phone: str

class EmailPayload(BaseModel):
    recipient_email: str
    subject: str
    candidates: List[Candidate]

# -------------------- EMAIL HTML BUILDER --------------------

def build_html(candidates: List[Candidate]) -> str:
    rows = ""
    for c in candidates:
        rows += f"""
        <tr>
            <td>{c.name}</td>
            <td>{c.tags}</td>
            <td>{c.bio}</td>
            <td>{", ".join(c.skills)}</td>
            <td>{", ".join(c.badges)}</td>
            <td>{c.coding_hours}</td>
            <td>{c.projects_completed}</td>
            <td><strong>{c.top_project.name}</strong><br>{c.top_project.description}<br><a href="{c.top_project.link}">View Project</a></td>
            <td>{", ".join(c.certifications)}</td>
            <td>{c.looking_for.type} | {c.looking_for.location} | {c.looking_for.duration}</td>
            <td>{c.email}</td>
            <td>{c.phone}</td>
            <td>{c.cgpa}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html><head>
    <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.5; color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; font-size: 14px; }}
    th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
    </style></head><body>
    <h2>Hello Recruiter,</h2>
    <p>Here is the list of shortlisted candidates:</p>
    <table>
        <thead>
            <tr><th>Name</th><th>Tags</th><th>Bio</th><th>Skills</th><th>Badges</th>
            <th>Coding Hours</th><th>Projects Completed</th><th>Top Project</th>
            <th>Certifications</th><th>I'm Looking For</th><th>Email</th><th>Phone</th><th>CGPA</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <p>Regards,<br><strong>Polaris Campus Team</strong></p>
    </body></html>
    """

# -------------------- EMAIL ENDPOINT --------------------

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailPayload):
    print("🚀 CLEAN version without recipient_name")
    print("📦 Incoming recipient:", payload.recipient_email)

    api_key = os.getenv("CLASSPLUS_EMAIL_API_KEY")
    print("🔐 Loaded API Key:", "✔️ Found" if api_key else "❌ Missing")

    if not api_key:
        raise HTTPException(status_code=500, detail="Missing email API key")

    try:
        email_body = build_html(payload.candidates)

        final_payload = {
            "orgId": 170,
            "senderId": 1,
            "service": 14,
            "email": {
                "to": [payload.recipient_email],
                "cc": [],
                "from": "pst@ce.classplus.co",
                "templateData": [],
                "subject": payload.subject,
                "content": email_body
            },
            "priority": "P2",
            "uuid": f"polaris-{payload.recipient_email}-{os.urandom(4).hex()}"
        }

        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=final_payload,
            headers={
                "Content-Type": "application/json",
                "api_key": api_key
            }
        )

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        return {"status": "❌ Exception", "details": str(e)}
