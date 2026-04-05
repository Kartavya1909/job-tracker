import os
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .models import Application, Company, StatusHistory
import datetime

JOB_KEYWORDS = {
    'applied': [
        'application received', 'thank you for applying',
        'we received your application', 'successfully applied',
        'application submitted', 'thank you for your interest',
        'your application has been', 'applied successfully'
    ],
    'oa': [
        'online assessment', 'coding assessment', 'hackerrank',
        'codility', 'online test', 'assessment link',
        'complete the assessment', 'technical assessment',
        'amcat', 'cocubes', 'elitmus', 'mettl'
    ],
    'interview': [
        'interview scheduled', 'interview invitation',
        'invited for interview', 'schedule your interview',
        'interview call', 'technical round', 'hr round',
        'zoom link', 'meet link', 'interview on', 'interview at'
    ],
    'offered': [
        'offer letter', 'pleased to offer',
        'job offer', 'we are delighted', 'offer of employment',
        'welcome to the team', 'joining date'
    ],
    'rejected': [
        'unfortunately', 'not moving forward', 'not selected',
        'regret to inform', 'other candidates',
        'position has been filled', 'we will not be',
        'not shortlisted', 'not been selected'
    ],
}

# keywords that must appear for an email to even be considered job-related
JOB_SIGNAL_WORDS = [
    'application', 'interview', 'offer', 'assessment', 'hiring',
    'recruitment', 'position', 'role', 'candidate', 'shortlist',
    'placement', 'internship', 'stipend', 'ctc', 'joining',
    'selected', 'rejected', 'unfortunately', 'congratulations'
]

IGNORE_DOMAINS = [
    'slack.com', 'railway.app', 'github.com', 'youtube.com',
    'swiggy.com', 'zomato.com', 'hotstar.com', 'netflix.com',
    'medium.com', 'substack.com', 'notion.so', 'figma.com',
    'vercel.com', 'netlify.com', 'pinterest.com', 'instagram.com',
    'twitter.com', 'facebook.com', 'whatsapp.com', 'spotify.com',
]

def is_job_related_sender(sender):
    sender_lower = sender.lower()
    for domain in IGNORE_DOMAINS:
        if domain in sender_lower:
            return False
    return True

def is_job_related_content(subject, body):
    text = (subject + ' ' + body).lower()
    for word in JOB_SIGNAL_WORDS:
        if word in text:
            return True
    return False

def classify_email(subject, body):
    text = (subject + ' ' + body).lower()
    for keyword in JOB_KEYWORDS['rejected']:
        if keyword in text:
            return 'rejected'
    for status in ['offered', 'interview', 'oa', 'applied']:
        for keyword in JOB_KEYWORDS[status]:
            if keyword in text:
                return status
    return None

def extract_ctc(body):
    patterns = [
        r'(?:ctc|salary|stipend|package)[^\d]*?([\d,.]+\s*(?:lpa|l\.p\.a|lakh|lac|per annum|/month|pm|per month))',
        r'([\d,.]+\s*(?:lpa|l\.p\.a|lakh|lac))',
        r'(?:inr|₹|rs\.?)\s*([\d,.]+)',
        r'([\d,.]+)\s*(?:per month|/month|pm)\b',
    ]
    body_lower = body.lower()
    for pattern in patterns:
        match = re.search(pattern, body_lower)
        if match:
            return match.group(1).strip()
    return ''

def extract_company_from_email(sender):
    match = re.search(r'@([\w\.-]+)', sender)
    if not match:
        return None
    domain = match.group(1).lower()
    parts = domain.split('.')
    if len(parts) >= 2:
        company_name = parts[-2].capitalize()
    else:
        company_name = parts[0].capitalize()
    return company_name

def get_email_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    else:
        data = payload['body'].get('data', '')
        if data:
            body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body

def sync_gmail(user, credentials_dict):
    creds = Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes'],
    )

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=50,
        q='is:unread'
    ).execute()

    messages = results.get('messages', [])
    synced = 0

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        body = get_email_body(msg_data['payload'])
        message_id = msg['id']

        # skip ignored domains
        if not is_job_related_sender(sender):
            continue

        # skip emails with no job signal words at all
        if not is_job_related_content(subject, body):
            # exception: placement cell emails always pass
            if not ('placement' in sender.lower() or 'soa' in sender.lower()):
                continue

        status = classify_email(subject, body)

        if not status:
            if 'placement' in sender.lower() or 'soa' in sender.lower():
                status = 'applied'

        if not status:
            continue

        company_name = extract_company_from_email(sender)
        if not company_name:
            continue

        ctc = extract_ctc(body)
        gmail_link = f'https://mail.google.com/mail/u/0/#inbox/{message_id}'

        company, _ = Company.objects.get_or_create(name=company_name)

        existing = Application.objects.filter(
            user=user,
            company=company
        ).first()

        if existing:
            if existing.status != status:
                StatusHistory.objects.create(
                    application=existing,
                    old_status=existing.status,
                    new_status=status,
                    note=f'Auto-updated from Gmail: {subject[:100]}'
                )
                existing.status = status
            if ctc and not existing.ctc:
                existing.ctc = ctc
            if not existing.gmail_message_id:
                existing.gmail_message_id = message_id
            existing.save()
        else:
            Application.objects.create(
                user=user,
                company=company,
                role='(detected from Gmail)',
                status=status,
                date_applied=datetime.date.today(),
                notes=f'Auto-created from Gmail. Subject: {subject[:200]}',
                ctc=ctc,
                gmail_message_id=message_id
            )

        synced += 1

    return synced