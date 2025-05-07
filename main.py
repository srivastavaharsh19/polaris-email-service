from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
from jinja2 import Template

app = FastAPI()

# Enable CORS for Bolt or Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your Netlify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class TopProject(BaseModel):
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
    Skills: Optional[List[str]]
    Badges: Optional[List[str]]
    CGPA: Optional[float]
    Certifications: Optional[List[str]]
    Coding_Hours: int
    Projects_Completed: int
    Top_Project: Optional[TopProject]
    Looking_For: LookingFor
    Email: str
    Phone: str

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:", payload.dict())

    # Inline HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.5; color: #333; }
            table { border-collapse: collapse; width: 100%; margin-top: 16px; font-size: 14px; }
            th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #f5f5f5; }
            h2 { color: #1a1a1a; }
            p.footer { margin-top: 24px; }
        </style>
    </head>
    <body>
        <h2>Hello {{ recipient_name }},</h2>
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
                {% for c in candidates %}
                <tr>
                    <td>{{ c.Name }}</td>
                    <td>{{ c.Tags or '' }}</td>
                    <td>{{ c.Bio or '' }}</td>
                    <td>{{ c.Skills | join(', ') if c.Skills else '' }}</td>
                    <td>{{ c.Badges | join(', ') if c.Badges else '' }}</td>
                    <td>{{ c.Coding_Hours }}</td>
                    <td>{{ c.Projects_Completed }}</td>
                    <td>
                        {% if c.Top_Project %}
                            <strong>{{ c.Top_Project.name }}</strong><br>
                            {{ c.Top_Project.description }}<br>
                            <a href="{{ c.Top_Project.link }}">View Project</a>
                        {% endif %}
                    </td>
                    <td>{{ c.Certifications | join(', ') if c.Certifications else '' }}</td>
                    <td>
                        {{ c.Looking_For.location }} |
                        {{ c.Looking_For.type }} |
                        {{ c.Looking_For.duration }}
                    </td>
                    <td>{{ c.Email }}</td>
                    <td>{{ c.Phone }}</td>
                    <td>{{ c.CGPA }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <p class="footer">
            Best regards,<br>
            <strong>Polaris Campus Team</strong>
        </p>
    </body>
    </html>
    """

    # Render HTML using Jinja2
    template = Template(html_template)
    html_content = template.render(recipient_name=payload.recipient_name, candidates=payload.candidates)

    # Final payload for internal Classplus email API
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
        "uuid": "polaris-2025-final-push"
    }

    headers = {
        "accessKey": "N6FPaqWCG58jH0d7u7Qoh7xTugP5Mw_IJQGjbRnQXKuImDL-9hCaVFQg",
        "Content-Type": "application/json"
    }

    print("📦 Final Payload:", data)

    try:
        response = requests.post("https://ce-api.classplus.co/v3/Communications/email/internal/superuser", json=data, headers=headers)
        print("📨 Status Code:", response.status_code)
        print("📨 Response:", response.text)

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
