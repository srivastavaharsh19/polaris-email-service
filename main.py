from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

app = FastAPI()

# Allow frontend (Bolt/Netlify) origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later to your Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- DATA SCHEMA --------------------
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
    recipient_name: str
    subject: str
    candidates: List[Candidate]

# -------------- EMAIL HTML GENERATOR ---------------
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
            <td><strong>{c.Top_Project.name}</strong><br>{c.Top_Project.description}<br><a href="{c.Top_Project.link}">View Project</a></td>
            <td>{", ".join(c.Certifications)}</td>
            <td>{c.Looking_For.type} | {c.Looking_For.location} | {c.Looking_For.duration}</td>
            <td>{c.Email}</td>
            <td>{c.Phone}</td>
            <td>{c.CGPA}</td>
        </tr>"""
    
    return f"""
    <!DOCTYPE html><html><head><style>
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

# ----------------- ENDPOINT -----------------------
@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailPayload, x_api_key: Optional[str] = Header(None)):
    expected_api_key = os.getenv("CLASSPLUS_EMAIL_API_KEY")

    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

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

        # ✅ Corrected: Use 'api_key' header for Classplus internal API
        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=final_payload,
            headers={
                "Content-Type": "application/json",
                "api_key": os.getenv("CLASSPLUS_EMAIL_API_KEY")
            }
        )

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        return {"status": "❌ Exception", "details": str(e)}
