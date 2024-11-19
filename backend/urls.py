from django.urls import path

from .views import (resume_creator)

urlpatterns = [
    path("resume-creator/", resume_creator, name="resume_creator"),
]