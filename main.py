from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Allow Bolt to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define candidate schema
class Candidate(BaseModel):
    Name: str
    Tags: str = ""
    Bio: str
    Skills: list
    Badges: str = ""
    Coding_Hours: int
    Projects_Completed: int
    Top_Project_Name: str
    Top_Project_Desc: str
    Top_Project_Link: str
    Certification_Title: str = ""
    Internship_Type: str = ""
    Internship_Location: str = ""
    Internship_Duration: str = ""
    Email: str
    Phone: str
    CGPA: float

# Define email payload schema
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: list[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:", payload.dict())

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

    for c in payload.candidates:
        skills = ", ".join(c.Skills)
        top_project_html = f"<strong>{c.Top_Project_Name}</strong><br>{c.Top_Project_Desc}<br><a href='{c.Top_Project_Link}'>View Project</a>"
        looking_for = f"{c.Internship_Location} | {c.Internship_Type} | {c.Internship_Duration}"
        html_content += f"""
            <tr>
                <td>{c.Name}</td>
                <td>{c.Tags}</td>
                <td>{c.Bio}</td>
                <td>{skills}</td>
                <td>{c.Badges}</td>
                <td>{c.Coding_Hours}</td>
                <td>{c.Projects_Completed}</td>
                <td>{top_project_html}</td>
                <td>{c.Certification_Title}</td>
                <td>{looking_for}</td>
                <td>{c.Email}</td>
                <td>{c.Phone}</td>
                <td>{c.CGPA}</td>
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

    # Classplus mail API
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
        "uuid": "polaris-2025-final-schema"
    }

    headers = {
        "accessKey": "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://ce-api.classplus.co/v3/Communications/email/internal/superuser",
            json=data,
            headers=headers
        )
        return {
            "status": "✅ Sent successfully" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }
    except Exception as e:
        return {
            "status": "❌ Failed to send",
            "details": str(e)
        }
