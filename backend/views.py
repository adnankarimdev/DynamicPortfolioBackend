from django.http import HttpResponse
from django.http import HttpResponse
import fitz  # PyMuPDF
import io
import os
from dotenv import load_dotenv
from collections import defaultdict
from django.views.decorators.http import require_http_methods
import time
import re
import json
import hashlib
from collections import Counter
from django.db.models import Q
from django.utils import timezone
from django.forms.models import model_to_dict
from django.core import serializers
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import pickle
from .serializers import (
    UserSerializer,
)

from .models import (
    CustomUser
)
# from langchain.vectorstores import FAISS
# from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from rest_framework import status
from rest_framework.response import Response
import jwt
import secrets
import googlemaps
import requests
from django.conf import settings
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from token_count import TokenCount
from datetime import datetime
import pytz
from twilio.rest import Client
from backend.prompts import (prompt_resume_creator)
tc = TokenCount(model_name="gpt-4o-mini")

# llm = ChatOpenAI(
#     model="gpt-4o",
#     temperature=1,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


SECRET_KEY = settings.SECRET_KEY


@csrf_exempt
def get_website_details(request):
    # Get the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token missing or invalid"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        # Decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded_token.get("email")  # Extract the email from the decoded token

        # Retrieve the user data using the email
        user = CustomUser.objects.get(email=email)  # Use the email field
        data_to_return = user.data
        return JsonResponse({"content": data_to_return}, status=200)

    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
@csrf_exempt
def save_website_details(request):
    if request.method == "POST":
        try:
            # Parse the JSON body of the request
            data = json.loads(request.body)
            website_data = data.get("data")
            user_token = data.get("userToken")

            if not website_data or not user_token:
                return JsonResponse(
                    {"error": "Missing data or user token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Decode the JWT token to extract the email
            try:
                decoded_token = jwt.decode(
                    user_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_email = decoded_token.get("email")
            except jwt.ExpiredSignatureError:
                return JsonResponse(
                    {"error": "Token has expired"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            except jwt.InvalidTokenError:
                return JsonResponse(
                    {"error": "Invalid token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve the user from the database
            try:
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                return JsonResponse(
                    {"error": "User not found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the website data
            user.data = website_data
            email_username = user.email.split('@')[0]
            user.url = "http://localhost:5000/" + email_username
            user.save()

            return JsonResponse(
                {"message": "Website details saved successfully"}, 
                status=status.HTTP_200_OK
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return JsonResponse(
            {"error": "Invalid HTTP method"}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

@csrf_exempt
def sign_up_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Save the new user
            user = serializer.save()

            # Generate the JWT token after user creation
            token = jwt.encode(
                {"email": user.email, "exp": datetime.utcnow() + timedelta(hours=24)},  # 24-hour expiry
                SECRET_KEY,
                algorithm="HS256",
            )

            # Return user data along with the JWT token
            return JsonResponse(
                {
                    "message": "User created successfully",
                    "token": token,
                    "user": {
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
    
@csrf_exempt
def log_in_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Generate a token (if using JWT)
            token = jwt.encode({"email": user.email, "exp": datetime.utcnow() + timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")

            return JsonResponse(
                {
                    "message": "Logged in successfully",
                    "token": token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                },
                status=200,
            )
        else:
            return JsonResponse(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def resume_creator(request):
    global prompt_resume_creator
    tokens = tc.num_tokens_from_string(prompt_resume_creator)
    print(f"journey analysis with badges INPUT: Tokens in the string: {tokens}")

    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        print(data)
        user_query = data.get("resumeContent", "")

        print(user_query)

        messages = [
            ("system", prompt_resume_creator),
            ("human", json.dumps(user_query)),
        ]

        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(ai_msg.content)
        print(f"journey analysis OUTPUT: Tokens in the string: {tokens}")

        # Try parsing the response content as JSON
        try:
            content = json.loads(ai_msg.content)
        except json.JSONDecodeError:
            # If parsing fails, return the content as a string
            return JsonResponse({"error": "Invalid JSON response from LLM", "content": ai_msg.content}, status=500)

        return JsonResponse({"content": content})

    return JsonResponse({"error": "Invalid request method"}, status=400)



def create_portfolio(resume):
        messages = [
            ("system", prompt_resume_creator),
            ("human", resume),
        ]

        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(ai_msg.content)
        print(f"journey analysis OUTPUT: Tokens in the string: {tokens}")

        # Try parsing the response content as JSON
        try:
            content = json.loads(ai_msg.content)
        except json.JSONDecodeError:
            # If parsing fails, return the content as a string
            return "error"

        return content
@csrf_exempt
def pdf_data(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        uploaded_file = request.FILES['pdf']
        
        # Read the uploaded file directly into memory
        file_bytes = uploaded_file.read()
        
        try:
            # Open the PDF file from memory using PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Return the extracted text as a response
            content = create_portfolio(text)
            return JsonResponse({"content": content})
        
        except Exception as e:
            # Catch errors and return them in the response
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No PDF file uploaded"}, status=400)