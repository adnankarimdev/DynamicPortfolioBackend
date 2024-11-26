from django.urls import path

from .views import (resume_creator, pdf_data, log_in_user, sign_up_user, save_website_details, get_website_details, get_website_details_by_url, upload_profile_picture)

urlpatterns = [
    path("resume-creator/", resume_creator, name="resume_creator"),
    path("pdf-data/", pdf_data, name="pdf_data"),
    path("login/", log_in_user, name="log_in_user"),
    path("sign-up/", sign_up_user, name="sign_up_user"),
    path("save-website-details/", save_website_details, name="save_website_details"),
    path("get-website-details/", get_website_details, name="get_website_details"),
    path("upload-profile-picture/", upload_profile_picture, name="upload_profile_picture"),
    path("get-website-details-by-url/<str:slug>/", get_website_details_by_url, name="get_website_details_by_url"),
]