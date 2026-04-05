from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_application, name='add_application'),
    path('update/<int:pk>/', views.update_status, name='update_status'),
    path('delete/<int:pk>/', views.delete_application, name='delete_application'),
    path('detail/<int:pk>/', views.application_detail, name='application_detail'),
]