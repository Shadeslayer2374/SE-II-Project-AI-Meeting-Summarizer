from django.urls import path
from . import views

urlpatterns = [
    path('members/',views.start,name='start'),
    
]
