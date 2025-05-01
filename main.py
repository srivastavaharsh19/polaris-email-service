from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: list  # List of dicts with all student details

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:", payload.dict())

    # Compose HTML table
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.5; color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 16px; font-size: 14px; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; vertical-align: top; }}
            th {{ background-color: #f5f5f5; }}
            h2 {{ color: #1a1a1a; }}
            p.footer {{ margin-top: 24px; }}
            a {{ color: #2a7ae2; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h2>Hello {payload.recipient_name},</h2>
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
                    <th>Email</th>
                    <th>Phone</th>
                </tr>
            </thead>
            <tbody>
    """

    for c in payload.candidates:
        top_project_html = ""
        if c.get("Top_Project_Name"):
            top_project_html = f"<strong>{c['Top_Project_Name']}</strong><br>{c.get('Top_Project_Description', '')}"
            if c.get("Top_Project_Link"):
                top_project_html += f'<br><a href="{c["Top_Project_Link"]}" target="_blank">View Project</a>'

        html_content += f"""
            <tr>
                <td>{c.get("Name", "")}</td>
                <td>{c.get("Tags", "")}</td>
                <td>{c.get("Bio", "")}</td>
                <td>{', '.join(c.get("Skills", []))}</td>
                <td>{c.get("Badges", "")}</td>
                <td>{c.get("Coding_Hours", "")}</td>
                <td>{c.get("Projects_Completed", "")}</td>
                <td>{top_project_html}</td>
                <td>{c.get("Email", "")}</td>
                <td>{c.get("Phone", "")}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
        <p class="footer">
            Best regards,<br>
            <strong>Polaris Campus Team</strong>
        </p>
    </body>
    </html>
    """

    # Prepare payload for internal API
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
        "uuid": "polaris-2025-shortlist"
    }

    headers = {
        "accessKey": "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg",
        "Content-Type": "application/json"
    }

    api_url = "https://ce-api.classplus.co/v3/Communications/email/internal/superuser"

    print("📦 Final Payload:", data)
    print("🚀 Headers:", headers)

    try:
        response = requests.post(api_url, json=data, headers=headers)
        print("📨 Status Code:", response.status_code)
        print("📨 Response:", response.text)

        return {
            "status": "✅ Sent successfully" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }
    except Exception as e:
        print("❌ Error while sending email:", str(e))
        return {
            "status": "❌ Failed to send",
            "details": str(e)
        }
