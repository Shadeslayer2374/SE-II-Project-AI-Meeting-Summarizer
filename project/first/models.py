from django.db import models
import datetime
from django.conf import settings
import os
import uuid

# Create your models here.

class Account(models.Model):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    name = models.CharField(max_length=50)
    Email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=128) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_data = models.JSONField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True, default=None)
    otp_created_at = models.DateTimeField(blank=True, null=True) 
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    uploads = models.IntegerField(default=0)    
    def __str__(self):
        return self.name

def pdf_upload_path(instance, filename):
    # This will create paths like: pdfs/user_1/filename.pdf
    return os.path.join('pdfs', f'user_{instance.user.user_id}', filename)

class Pdf(models.Model):
    pdf_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,default="Untitled")  # Added missing field definition
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to=pdf_upload_path)  # Stores the PDF file
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF {self.pdf_id} by {self.user.name}"
