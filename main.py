from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS config
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML email template (inline)
def build_html(recipient_name: str, candidates: list):
    def row(c):
        top_project = c.get("Top_Project", {})
        certs = ", ".join(c.get("Certifications", [])) or "—"
        looking = c.get("Looking_For", {})
        return f"""
        <tr>
            <td>{c.get("Name", "")}</td>
            <td>{c.get("Tags", "")}</td>
            <td>{c.get("Bio", "")}</td>
            <td>{", ".join(c.get("Skills", []))}</td>
            <td>{", ".join(c.get("Badges", []))}</td>
            <td>{c.get("Coding_Hours", "")}</td>
            <td>{c.get("Projects_Completed", "")}</td>
            <td>
                <strong>{top_project.get("name", "")}</strong><br>
                {top_project.get("description", "")}<br>
                <a href="{top_project.get("link", "")}">View Project</a>
            </td>
            <td>{certs}</td>
            <td>{looking.get("location", "")} | {looking.get("type", "")} | {looking.get("duration", "")}</td>
            <td><a href="mailto:{c.get("Email", "")}">{c.get("Email", "")}</a></td>
            <td>{c.get("Phone", "")}</td>
            <td>{c.get("CGPA", "")}</td>
        </tr>
        """

    table_rows = "".join([row(c) for c in candidates])

    return f"""
    <html>
    <body style="font-family: sans-serif;">
        <h2>Hello {recipient_name},</h2>
        <p>Here is the list of shortlisted candidates for your review:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-size: 14px;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th>Name</th><th>Tags</th><th>Bio</th><th>Skills</th><th>Badges</th>
                    <th>Coding Hours</th><th>Projects Completed</th><th>Top Project</th>
                    <th>Certifications</th><th>I'm Looking For</th><th>Email</th><th>Phone</th><th>CGPA</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        <p><br>Best regards,<br><strong>Polaris Campus Team</strong></p>
    </body>
    </html>
    """

@app.post("/send_candidate_list_email/")
async def send_candidate_list_email(request: Request):
    payload = await request.json()
    recipient_email = payload.get("recipient_email")
    recipient_name = payload.get("recipient_name")
    subject = payload.get("subject", "Shortlisted Candidates")
    candidates = payload.get("candidates", [])

    print("✅ Received payload:", payload)

    html_content = build_html(recipient_name, candidates)

    email_api = "https://ce-api.classplus.co/v3/Communications/email/internal/superuser"
    api_key = os.environ.get("CLASSPLUS_EMAIL_API_KEY")

    if not api_key:
        print("❌ Missing API key")
        return {"status": "❌ API key missing"}

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    data = {
        "to": recipient_email,
        "subject": subject,
        "message": html_content,
        "from": "pst@ce.classplus.co",
        "name": "Polaris Campus Team",
    }

    try:
        response = requests.post(email_api, json=data, headers=headers)
        print("📬 Status Code:", response.status_code)
        print("📬 Response:", response.text)

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return {
            "status": "❌ Exception",
            "details": str(e)
        }
