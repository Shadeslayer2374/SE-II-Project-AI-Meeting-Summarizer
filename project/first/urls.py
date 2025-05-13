from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
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
    
    path('check_pdf_status/<uuid:file_id>/', views.check_pdf_status, name='check_pdf_status'),
    path('pdf-viewer/', views.pdf_viewer, name='pdf_viewer'),
    path('download_pdf/<uuid:file_id>/', views.download_pdf, name='download_pdf'),
    path('process-file/', views.process_file, name='process_file'),
    path('delete-pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)