from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS for Bolt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
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

    # Build HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; color: #333; line-height: 1.5; }
            table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }
            th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #f5f5f5; }
            a { color: #2a7ae2; text-decoration: none; }
            p.footer { margin-top: 24px; }
        </style>
    </head>
    <body>
        <h2>Hello {recipient_name},</h2>
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
    """.replace("{recipient_name}", payload.recipient_name)

    for c in payload.candidates:
        html += f"""
            <tr>
                <td>{c.get('Name', '')}</td>
                <td>{c.get('Tags', '')}</td>
                <td>{c.get('Bio', '')}</td>
                <td>{', '.join(c.get('Skills', []))}</td>
                <td>{c.get('Badges', '')}</td>
                <td>{c.get('Coding_Hours', '')}</td>
                <td>{c.get('Projects_Completed', '')}</td>
                <td><strong>{c.get('Top_Project_Name', '')}</strong><br>{c.get('Top_Project_Description', '')}<br><a href="{c.get('Top_Project_Link', '#')}">View Project</a></td>
                <td>{c.get('Certifications', '')}</td>
                <td>{c.get('Internship_Preferences', '')}</td>
                <td>{c.get('Email', '')}</td>
                <td>{c.get('Phone', '')}</td>
                <td>{c.get('CGPA', '')}</td>
            </tr>
        """

    html += """
            </tbody>
        </table>
        <p class="footer">
            Best regards,<br>
            <strong>Polaris Campus Team</strong>
        </p>
    </body>
    </html>
    """

    # Prepare email payload for internal API
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
            "content": html,
            "attachmentUrls": []
        },
        "priority": "P2",
        "uuid": "polaris-2025-full-final"
    }

    headers = {
        "accessKey": "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg",
        "Content-Type": "application/json"
    }

    # Debug logs
    print("🔑 API Key Loaded")
    print("📬 Sending from:", data["email"]["from"])
    print("📬 Sending to:", data["email"]["to"])
    print("📦 Payload:", data)

    # Make POST request
    try:
        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=data,
            headers=headers
        )
        print("📨 Status Code:", response.status_code)
        print("📨 Response:", response.text)
        return {
            "status": "✅ Sent successfully" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }
    except Exception as e:
        print("❌ Exception:", str(e))
        return {
            "status": "❌ Error occurred",
            "details": str(e)
        }
