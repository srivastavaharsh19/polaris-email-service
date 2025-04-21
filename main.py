from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Enable CORS for Bolt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with specific domain
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
        <h2>Hello {payload.recipient_name},</h2>
        <p>Here is the list of shortlisted candidates for your review:</p>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>College</th>
                    <th>Degree</th>
                    <th>Skills</th>
                    <th>Coding Hours</th>
                    <th>Projects</th>
                </tr>
            </thead>
            <tbody>
    """

    for candidate in payload.candidates:
        html_content += f"""
            <tr>
                <td>{candidate['Name']}</td>
                <td>{candidate['College']}</td>
                <td>{candidate['Degree']}</td>
                <td>{", ".join(candidate['Skills'])}</td>
                <td>{candidate['Coding_Hours']}</td>
                <td>{candidate['Projects']}</td>
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

    # Prepare payload for Classplus internal API
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
        "uuid": "polaris-2025-shortlist-test"
    }

    # Hardcoded Classplus Email API credentials
    access_key = "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg"
    api_url = "https://ce-api.classplus.co/v3/Communications/email/internal/superuser"
    
    headers = {
        "accessKey": access_key,
        "Content-Type": "application/json"
    }

    print("📧 Type of from_email:", type(data["email"]["from"]))
    print("📧 Type of from_name:", type(payload.recipient_name))
    print("🔑 Debug: Loaded API Key =", access_key)
    print("🔗 Debug: Loaded API URL =", api_url)
    print("📬 From Email:", data["email"]["from"])
    print("📬 To Email:", data["email"]["to"])
    print("📦 Final Payload Sent to Classplus Email API:", data)
    print("🚀 Headers:", headers)

    # Send the request
    try:
        response = requests.post(api_url, json=data, headers=headers)
        print("📨 Status Code:", response.status_code)
        print("📨 Response:", response.text)

        return {
            "status": "✅ Sent successfully" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }
    except Exception as e:
        print("❌ Exception occurred while sending email:", str(e))
        return {
            "status": "❌ Failed to send",
            "details": str(e)
        }
