from django.urls import path

from .views import (resume_creator, pdf_data, log_in_user, sign_up_user)

urlpatterns = [
    path("resume-creator/", resume_creator, name="resume_creator"),
    path("pdf-data/", pdf_data, name="pdf_data"),
    path("login/", log_in_user, name="log_in_user"),
    path("sign-up/", sign_up_user, name="sign_up_user"),
]