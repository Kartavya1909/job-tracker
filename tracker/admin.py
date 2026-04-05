from django.contrib import admin
from .models import Company, Application, StatusHistory

admin.site.register(Company)
admin.site.register(Application)
admin.site.register(StatusHistory)