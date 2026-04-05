import os
import requests as http_requests
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_auth_url(redirect_uri, state):
    params = {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }
    base_url = 'https://accounts.google.com/o/oauth2/auth'
    param_string = '&'.join(f'{k}={v}' for k, v in params.items())
    return f'{base_url}?{param_string}'

def exchange_code_for_token(code, redirect_uri):
    response = http_requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
    )
    return response.json()

def credentials_to_dict(token_data, redirect_uri):
    return {
        'token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token'),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'scopes': SCOPES,
    }