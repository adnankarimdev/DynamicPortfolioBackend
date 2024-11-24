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
from supabase import create_client, Client
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


url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)


@csrf_exempt
def get_website_details_by_url(request, slug):
    try:
        # Retrieve the user data using the email
        user_url = "http://localhost:5000/" + slug
        response = supabase.table("user_data").select("*").eq('url', user_url).execute()
        data_to_return = response.data[0]['data']
        return JsonResponse({"content": data_to_return}, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
@csrf_exempt
def get_website_details(request):
    # Get the Authorization header
    # NEED TO ADD VALIDATION WITH SUPABASE
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token missing or invalid"}, status=401)

    token = auth_header.split(" ")[1]
    response = supabase.table("user_data").select("*").eq('id', token).execute()
    if response.data[0]['data'] is None:
        return JsonResponse({"content": {}}, status=200)
    return JsonResponse({"content": response.data[0]['data']}, status=200)

    
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
                    status=400
                )

            # Retrieve the user from the Supabase 'user_data' using the user_token (UUID)
            response = supabase.table('user_data').select('*').eq('id', user_token).execute()

            if len(response.data) == 0:
                return JsonResponse(
                    {"error": "User not found"}, 
                    status=400
                )
            # Extract the user data from the response
            user = response.data[0]

            # Save the website data and generate the URL
            email_username = user['email'].split('@')[0]
            user_url = f"http://localhost:5000/{email_username}"

            # Update the user in the Supabase 'user_data' with the website data and URL
            update_response = supabase.table('user_data').update({
                'data': website_data, 
                'url': user_url
            }).eq('id', user['id']).execute()

            return JsonResponse(
                {"message": "Website details saved successfully", "url": user_url}, 
                status=200
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, 
                status=400
            )
    else:
        return JsonResponse(
            {"error": "Invalid HTTP method"}, 
            status=405
        )

@csrf_exempt
def sign_up_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=400
            )

        email = data.get("email")
        password = data.get("password")

        # Step 1: Use Supabase's auth.sign_up to create the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        # Step 2: Extract user details from the response
        user_data = response.user
        user_id = user_data.id  # Supabase user ID (UUID)

        #Step 3: swag
        insert_response = supabase.table('user_data').insert({
            'id': user_id,  # Use the UUID from authentication
            'email': email,  # Optional: Store email if needed
            'data': None,  # Leave other columns empty or set to None
            'url': None  # You can leave 'url' blank for now as well
        }).execute()

        # Step 3: Return the response with user information
        return JsonResponse(
            {
                "message": "User created successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                },
            },
            status=201,
        )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
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
        response = supabase.auth.sign_in_with_password({"email": email, "password":  password})
        user_data = response.user
        user_id = user_data.id  # Supabase user ID (UUID)
        print(user_data)
        return JsonResponse(
            {
                "message": "User logged in successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                },
            },
            status=201,
        )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
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
            print("Creating portfolio...")
            content = create_portfolio(text)
            return JsonResponse({"content": content})
        
        except Exception as e:
            # Catch errors and return them in the response
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No PDF file uploaded"}, status=400)