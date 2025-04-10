from django.contrib import admin

# Register your models here.

from .models import Account, Pdf

admin.site.register(Account)
admin.site.register(Pdf)