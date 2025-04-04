from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.first, name='first'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),#
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'), 
    path('reset-password/', views.reset_password, name='reset_password'), 
    
    path('main/', views.main, name='main'),
    path('option/', views.option, name='option'),
    
    path('profile/', views.profile, name='profile'),
    path('aboutus/', views.aboutus, name='aboutus'),#
    
    path('process-file/', views.process_file, name='process_file'),
    path('check-pdf-status/<str:file_id>/', views.check_pdf_status, name='check_pdf_status'),
    path('download-pdf/<str:file_id>/', views.download_pdf, name='download_pdf'),
    path('pdf-viewer/', views.pdf_viewer, name='pdf_viewer'),
]