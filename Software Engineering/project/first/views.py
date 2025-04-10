from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.conf import settings
from django.views.decorators.http import require_http_methods, require_POST
from django.core.files import File
from django.urls import reverse

import datetime
import json
import os
import re
import time
import uuid
import tempfile

from .models import Account, Pdf
from .ai_code.functions import *
from django.db.models import F

import random 
import smtplib
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  

pdf_status = {}
emails_reset = []

def logout(request):
    request.session.flush() 
    messages.success(request, "You have been logged out.")
    return redirect('first') 

def aboutus(request):
    return render(request, "aboutus.html")

def profile(request):
    if 'user_id' in request.session:
        email = request.session.get('email')
        try:
            user = Account.objects.get(Email=email)
            pdfs = Pdf.objects.filter(user=user)
            context = {
                "name": user.name,
                "email": user.Email,
                "phone": user.phone_number,
                "gender": user.gender,
                "date": user.created_at.strftime("%b %d, %Y"),
                "uploads": user.uploads,
                "pdfs": pdfs,
            }
            return render(request, "profile.html", context)
        except Account.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login') 
    else:
        messages.error(request, "Please log in first.")
        return redirect('login')  

def first(request):
    return render(request, "first.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            if '@' in username:
                user = Account.objects.get(Email=username)
            else:
                user = Account.objects.get(phone_number=username)

            if check_password(password, user.password):
                request.session['user_id'] = user.user_id  
                request.session['email'] = user.Email
                request.session.set_expiry(3600)
                messages.success(request, f"Welcome, {user.name}!")
                return redirect('main')  
            else:
                messages.error(request, "Invalid password. Please try again.")
        except Account.DoesNotExist:
            messages.error(request, "User not found. Please sign up first.")

        return redirect('login') 

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        gender = request.POST.get('gender')

        if not all([name, email, phone, password, gender]):
            messages.error(request, "All fields are required!")
            return redirect('signup')

        if Account.objects.filter(Email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')

        user = Account.objects.create(
            name=name,
            Email=email,
            phone_number=phone,
            password=make_password(password),
            gender=gender
        )
        
        request.session['user_id'] = user.user_id
        request.session['email'] = email
        request.session.set_expiry(3600)
        messages.success(request, f"Welcome, {name}!")
        return redirect('main')
    
    return render(request, 'signup.html')

def main(request):
    if 'user_id' not in request.session: 
        messages.error(request, "Please log in first.")
        return redirect('login')
    return render(request, "main.html")

def option(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')
    return render(request, "option.html")

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not new_password or not confirm_password:
            messages.error(request, "Both fields are required.")
            return redirect('reset_password')  

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        if len(new_password) < 8 or not re.search(r'[A-Za-z]', new_password) or not re.search(r'[0-9]', new_password):
            messages.error(request, "Password must be at least 8 characters long and include both letters and numbers.")
            return redirect('reset_password')

        if not emails_reset:
            messages.error(request, "Session expired. Please start the password reset process again.")
            return redirect('forgot_password')

        try:
            user = Account.objects.get(Email=emails_reset[-1])  
            user.password = make_password(new_password)
            user.save()
            emails_reset.clear() 
            messages.success(request, "Your password has been successfully reset. Please log in.")
            return redirect('login') 
        except Account.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')

    return render(request, 'reset_password.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(Email=email)
            send_otp(user)
            messages.success(request, "OTP sent to your email.")
            emails_reset.append(email)
            return redirect('verify_otp') 
        except Account.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
    return render(request, 'forgot_password.html')

@csrf_exempt 
def send_otp(user):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.otp = otp
    user.otp_created_at = now()
    user.save()
        
    sender_email = "echoAI2026@outlook.com"
    sender_password = "AniLeviPrachi2026"
    receiver_email = user.Email
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}"
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print("OTP sent successfully")
    return

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')

        if not emails_reset:
            messages.error(request, "Session expired or invalid request.")
            return redirect('forgot_password')

        try:
            user = Account.objects.get(Email=emails_reset[-1])
            
            if not user.otp or not user.otp_created_at:
                messages.error(request, "OTP expired or not found. Please try again.")
                return redirect('forgot_password')

            expiry_time = user.otp_created_at + datetime.timedelta(minutes=5)
            if otp == user.otp and now() <= expiry_time:
                user.otp = None
                user.otp_created_at = None
                user.save()
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect('verify_otp')
        
        except Account.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('signup')

    return render(request, 'verify_otp.html')

@csrf_protect
def process_file(request):
    if request.method == 'POST':
        email = request.session.get('email')
        user = Account.objects.get(Email=email)
        try:
            file = request.FILES['file']
            file_type = request.POST.get('type')
            
            valid_types = {
                'video': ['.mp4', '.mkv', '.avi'],
                'audio': ['.mp3', '.wav', '.ogg'],
                'transcript': ['.txt', '.docx', '.pdf']
            }
            
            ext = os.path.splitext(file.name)[1].lower()
            if file_type not in valid_types or ext not in valid_types[file_type]:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid file type for {file_type}'
                }, status=400)
            
            file_id = str(uuid.uuid4())
            temp_dir = 'temp_uploads'
            os.makedirs(temp_dir, exist_ok=True)
            
            original_path = os.path.join(temp_dir, f'original_{file_id}{ext}')
            with open(original_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            pdf_status[file_id] = {
                'status': 'processing',
                'start_time': now(),
                'file_type': file_type,
                'user_id': user.user_id,
                'original_path': original_path,
                'temp_dir': temp_dir
            }
            
            try:
                if file_type == 'video':
                    pdf_path = process_video(original_path, file_id)
                elif file_type == 'audio':
                    pdf_path = process_audio(original_path, file_id)
                elif file_type == 'transcript':
                    pdf_path = process_transcript(original_path, file_id)
                
                if not os.path.exists(pdf_path):
                    raise Exception(f"Processing failed - no output PDF created for {file_type}")
                
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_record = Pdf(
                        name=f"{file_type.capitalize()} Summary - {file.name}",
                        user=user,
                        pdf_file=File(pdf_file, name=f'summary_{file_id}.pdf'))
                    pdf_record.save()
                
                pdf_status[file_id].update({
                    'status': 'ready',
                    'pdf_path': pdf_record.pdf_file.name,
                    'db_id': pdf_record.pk,
                    'pdf_url': reverse('download_pdf', kwargs={'file_id': file_id})
                })
                
                if os.path.exists(original_path):
                    os.remove(original_path)
                
                return JsonResponse({
                    'success': True,
                    'file_id': file_id,
                    'status_url': reverse('check_pdf_status', kwargs={'file_id': file_id}),
                    'viewer_url': f"{reverse('pdf_viewer')}?file_id={file_id}",
                    'download_url': reverse('download_pdf', kwargs={'file_id': file_id})
                })
                
            except Exception as processing_error:
                if 'pdf_path' in locals() and os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if os.path.exists(original_path):
                    os.remove(original_path)
                
                pdf_status[file_id]['status'] = 'failed'
                pdf_status[file_id]['message'] = str(processing_error)
                
                return JsonResponse({
                    'success': False,
                    'message': str(processing_error)
                }, status=500)
                
        except Exception as e:
            if 'original_path' in locals() and os.path.exists(original_path):
                os.remove(original_path)
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def check_pdf_status(request, file_id):
    try:
        file_id_str = str(file_id)
        status_info = pdf_status.get(file_id_str)
        
        if not status_info:
            return JsonResponse({
                'status': 'not_found',
                'message': 'File ID not found in processing queue'
            }, status=404)
        
        if status_info['status'] == 'processing':
            processing_time = (now() - status_info['start_time']).total_seconds()
            if processing_time > 600:
                status_info['status'] = 'failed'
                status_info['message'] = 'Processing timeout'
                
                if 'original_path' in status_info and os.path.exists(status_info['original_path']):
                    os.remove(status_info['original_path'])
        
        response_data = {
            'status': status_info.get('status'),
            'message': status_info.get('message', '')
        }
        
        if status_info.get('status') == 'ready':
            response_data.update({
                'pdf_url': status_info.get('pdf_url'),
                'db_id': status_info.get('db_id')
            })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def download_pdf(request, file_id):
    try:
        file_id_str = str(file_id)
        status_info = pdf_status.get(file_id_str)
        
        if not status_info or status_info.get('status') != 'ready':
            return JsonResponse({
                'error': 'PDF not ready or not found'
            }, status=404)
        
        pdf_record = get_object_or_404(Pdf, pk=status_info['db_id'])
        
        response = FileResponse(pdf_record.pdf_file)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = f'attachment; filename="EchoAI_Summary_{file_id}.pdf"'
        
        # Update user's upload count
        if 'email' in request.session:
            try:
                user = Account.objects.get(Email=request.session['email'])
                user.uploads = F('uploads') + 1
                user.save(update_fields=['uploads'])
            except Account.DoesNotExist:
                pass
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
    
def pdf_viewer(request):
    file_id = request.GET.get('file_id')
    if not file_id:
        return HttpResponse('File ID missing', status=400)
    
    try:
        status_info = pdf_status.get(str(file_id))
        if not status_info or status_info.get('status') != 'ready':
            return HttpResponse('PDF not ready', status=404)
        
        pdf_record = Pdf.objects.get(pk=status_info['db_id'])
        return render(request, 'pdfviewer.html', {
            'pdf_url': pdf_record.pdf_file.url,
            'file_id': file_id
        })
        
    except Pdf.DoesNotExist:
        return HttpResponse('PDF not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)