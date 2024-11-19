from django.urls import path

from .views import (resume_creator, pdf_data)

urlpatterns = [
    path("resume-creator/", resume_creator, name="resume_creator"),
    path("pdf-data/", pdf_data, name="pdf_data"),
]