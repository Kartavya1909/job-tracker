# Job Application Tracker

A full-stack Django web application to track placement and internship applications during campus hiring season. Automatically syncs with your Gmail inbox to detect and classify recruitment emails.

🔗 **Live Demo:** https://web-production-b36c1.up.railway.app
📁 **GitHub:** https://github.com/Kartavya1909/job-tracker

---

## Features

- **Gmail Auto-Sync** — Connects to your Gmail inbox via OAuth 2.0 and automatically detects job-related emails from recruiters and placement cells
- **Smart Email Classification** — Keyword-based classifier automatically categorizes emails into Applied, OA Received, Interview Scheduled, Offered, or Rejected
- **CTC / Stipend Extraction** — Automatically extracts salary or stipend information from offer emails using regex pattern matching
- **Status History Tracking** — Every status change is logged with timestamps and notes so you can see the full journey of each application
- **Follow-up Reminders** — Set follow-up dates on applications and get alerted on your dashboard when they're due
- **Open in Gmail** — Each auto-detected application links directly back to the original email
- **Filter by Status** — Quickly filter your dashboard to see only applications in a specific stage
- **User Authentication** — Each user has a private, secure dashboard with their own data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.x, Python 3.12 |
| Database | SQLite (local), PostgreSQL (production) |
| Authentication | Django Auth |
| Gmail Integration | Gmail API v1, OAuth 2.0 |
| HTTP Client | google-auth, google-api-python-client |
| Deployment | Railway |
| Frontend | Django Templates, HTML/CSS/JS |

---

## Project Structure

```
job-tracker/
├── core/                   # Django project settings and URLs
│   ├── settings.py
│   └── urls.py
├── tracker/                # Main application
│   ├── models.py           # Company, Application, StatusHistory
│   ├── views.py            # All views including Gmail OAuth flow
│   ├── urls.py
│   ├── gmail_auth.py       # OAuth 2.0 flow handler
│   ├── gmail_sync.py       # Gmail API sync + keyword classifier
│   ├── management/
│   │   └── commands/       # Django management commands
│   └── templates/
│       └── tracker/        # HTML templates
├── requirements.txt
├── Procfile
└── manage.py
```

---

## How Gmail Sync Works

1. User clicks **Sync Gmail** on the dashboard
2. App redirects to Google OAuth consent screen
3. After authorization, app fetches last 50 unread inbox emails
4. Each email is checked against an ignore list (Slack, GitHub, etc.)
5. Remaining emails are checked for job-signal words (application, interview, offer, etc.)
6. Matching emails are classified into a status using keyword matching
7. Company name is extracted from the sender's email domain
8. CTC/stipend is extracted from the email body using regex
9. Application is created or updated in the database with a link to the original email

---

## Local Setup

### Prerequisites

- Python 3.10+
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (Web Application type)

### Installation

```bash
# Clone the repo
git clone https://github.com/Kartavya1909/job-tracker
cd job-tracker

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Environment Variables

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
DEBUG=True
```

---

## Deployment (Railway)

The app is deployed on Railway with the following configuration:

**Procfile:**
```
web: python manage.py migrate && gunicorn core.wsgi --log-file -
```

**Environment variables** are set directly in Railway's dashboard — no secrets in the repository.

---

## Models

### Application
| Field | Type | Description |
|---|---|---|
| user | ForeignKey | Owner of the application |
| company | ForeignKey | Company applied to |
| role | CharField | Job title or position |
| status | CharField | applied / oa / interview / offered / rejected |
| date_applied | DateField | Date of application |
| follow_up_date | DateField | Optional reminder date |
| notes | TextField | Manual or auto-generated notes |
| ctc | CharField | Salary/stipend extracted from email |
| gmail_message_id | CharField | Links back to original Gmail message |

### StatusHistory
Logs every status change with old status, new status, timestamp, and a note.

---

## Roadmap

- [ ] Add PostgreSQL on Railway for persistent production database
- [ ] Periodic Gmail sync using Celery + Redis
- [ ] Analytics dashboard with charts (application funnel, success rate)
- [ ] Export applications to CSV
- [ ] Mobile-responsive UI improvements

---

## Author

**Kartavya** — B.Tech CSE Final Year, ITER, SOA University  
GitHub: [@Kartavya1909](https://github.com/Kartavya1909)
