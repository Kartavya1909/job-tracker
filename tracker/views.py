from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import Application, Company, StatusHistory
from datetime import date

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    total = applications.count()
    offered = applications.filter(status='offered').count()
    rejected = applications.filter(status='rejected').count()
    in_progress = applications.exclude(status__in=['offered', 'rejected']).count()
    follow_ups = applications.filter(follow_up_date__lte=date.today()).exclude(status__in=['offered', 'rejected'])
    return render(request, 'tracker/dashboard.html', {
        'applications': applications,
        'total': total,
        'offered': offered,
        'rejected': rejected,
        'in_progress': in_progress,
        'follow_ups': follow_ups,
    })

@login_required
def add_application(request):
    if request.method == 'POST':
        company_name = request.POST.get('company')
        company, _ = Company.objects.get_or_create(name=company_name)
        Application.objects.create(
            user=request.user,
            company=company,
            role=request.POST.get('role'),
            status=request.POST.get('status'),
            date_applied=request.POST.get('date_applied'),
            follow_up_date=request.POST.get('follow_up_date') or None,
            notes=request.POST.get('notes'),
        )
        messages.success(request, 'Application added successfully.')
        return redirect('dashboard')
    return render(request, 'tracker/add_application.html')

@login_required
def update_status(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status != application.status:
            StatusHistory.objects.create(
                application=application,
                old_status=application.status,
                new_status=new_status,
                note=request.POST.get('note', '')
            )
            application.status = new_status
            application.notes = request.POST.get('notes', application.notes)
            application.follow_up_date = request.POST.get('follow_up_date') or None
            application.save()
            messages.success(request, 'Status updated.')
        return redirect('dashboard')
    return render(request, 'tracker/update_status.html', {'application': application})

@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted.')
    return redirect('dashboard')

@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    history = application.history.order_by('-changed_at')
    return render(request, 'tracker/detail.html', {'application': application, 'history': history})