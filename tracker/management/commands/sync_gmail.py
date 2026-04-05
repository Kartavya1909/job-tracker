from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.gmail_sync import sync_gmail
import json

class Command(BaseCommand):
    help = 'Sync Gmail inbox for all users with connected Gmail'

    def handle(self, *args, **kwargs):
        from django.contrib.sessions.models import Session
        self.stdout.write('Gmail sync is triggered via the web interface.')