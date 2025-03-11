import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings
from django.template import loader
from django.http import HttpResponse


def start(request):
    template = loader.get_template("./templates/first.html")
    return HttpResponse(template.render())

# @csrf_exempt  # Temporarily disable CSRF for testing (use CSRF token in production)
# def upload_file(request):
#     if request.method == "POST" and request.FILES.get("file"):
#         uploaded_file = request.FILES["file"]
#         file_name = uploaded_file.name

#         # Define the storage directory
#         upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
#         os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists

#         # Save the file to the storage directory
#         file_path = os.path.join(upload_dir, file_name)
#         with open(file_path, "wb+") as destination:
#             for chunk in uploaded_file.chunks():
#                 destination.write(chunk)

#         return JsonResponse({"message": "File uploaded successfully!", "file_path": file_path})
    
#     return JsonResponse({"message": "No file received"}, status=400)

