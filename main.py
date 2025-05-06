from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Enable CORS for Bolt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: list

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:", payload.dict())

    # Compose HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.5; color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 16px; font-size: 14px; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            h2 {{ color: #1a1a1a; }}
            p.footer {{ margin-top: 24px; }}
        </style>
    </head>
    <body>
        <h2>Hello Recruiter,</h2>
        <p>Here is the list of shortlisted candidates for your review:</p>
        <table>
            <thead>
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
            </thead>
            <tbody>
    """

    for candidate in payload.candidates:
        name = candidate.get("Name", "—")
        tags = candidate.get("Tags", "—")
        bio = candidate.get("Bio", "—")
        skills = ", ".join(candidate.get("Skills", [])) if isinstance(candidate.get("Skills"), list) else candidate.get("Skills", "—")
        badges = ", ".join(candidate.get("Badges", [])) if isinstance(candidate.get("Badges"), list) else candidate.get("Badges", "—")
        certifications = ", ".join(candidate.get("Certifications", [])) if candidate.get("Certifications") else "—"
        internship = candidate.get("Internship Preferences", "—")
        email = candidate.get("Email", "—")
        phone = candidate.get("Phone", "—")
        cgpa = candidate.get("CGPA", "—")
        coding_hours = candidate.get("Coding Hours", "—")
        projects_completed = candidate.get("Projects Completed", "—")

        # Top Project
        project_data = candidate.get("Top Project", {})
        project_html = "—"
        if project_data:
            pname = project_data.get("Name", "")
            pdesc = project_data.get("Description", "")
            plink = project_data.get("Link", "#")
            project_html = f"<strong>{pname}</strong><br>{pdesc}<br><a href='{plink}'>View Project</a>"

        html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{tags}</td>
                <td>{bio}</td>
                <td>{skills}</td>
                <td>{badges}</td>
                <td>{coding_hours}</td>
                <td>{projects_completed}</td>
                <td>{project_html}</td>
                <td>{certifications}</td>
                <td>{internship}</td>
                <td>{email}</td>
                <td>{phone}</td>
                <td>{cgpa}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
        <p class='footer'>
            Best regards,<br>
            <strong>Polaris Campus Team</strong>
        </p>
    </body>
    </html>
    """

    # Prepare payload for Classplus internal email API
    data = {
        "orgId": 170,
        "senderId": 1,
        "service": 14,
        "email": {
            "to": [payload.recipient_email],
            "cc": [],
            "from": "pst@ce.classplus.co",
            "templateData": [],
            "subject": payload.subject,
            "content": html_content,
            "attachmentUrls": []
        },
        "priority": "P2",
        "uuid": "polaris-2025-final-candidate-email"
    }

    access_key = os.getenv("ACCESS_KEY", "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg")
    api_url = "https://ce-api.classplus.co/v3/Communications/email/internal/superuser"
    
    headers = {
        "accessKey": access_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=data, headers=headers)
        return {
            "status": "✅ Sent successfully" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }
    except Exception as e:
        return {
            "status": "❌ Failed to send",
            "details": str(e)
        }
