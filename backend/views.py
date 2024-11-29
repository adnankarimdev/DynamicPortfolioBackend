from django.http import HttpResponse
from django.http import HttpResponse
import stripe
import fitz  # PyMuPDF
import io
import os
from dotenv import load_dotenv
from collections import defaultdict
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
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
stripe.api_key = settings.STRIPE_API_KEY


@csrf_exempt
def upload_profile_picture(request):
    if request.method == "POST":
        file = request.FILES.get("file")  # Get the file from the request
        email = request.POST.get("email")  # Get the email from the request
        response = supabase.storage.list_buckets()
        response = supabase.storage.get_bucket('test_bucket')


        print(response)

        if not file or not email:
            return JsonResponse({"error": "File or email not provided"}, status=400)

        # Construct the path for the user's avatar
        file_path = f"public/{email}_avatar.png"
        # Save the file temporarily before uploading to Supabase
        temp_file_path = default_storage.save(file.name, file)

        # Check if a file already exists at the path
        existing_file_response = supabase.storage.from_("test_bucket").list(path="public")
        existing_files = [item['name'] for item in existing_file_response]
        
        if file_path.split("/")[-1] in existing_files:
            # File exists, update it
            with open(temp_file_path, "rb") as f:
                response = supabase.storage.from_("test_bucket").update(
                    file=f,
                    path=file_path,  # Save file with email identifier
                    file_options={"cache-control": "3600", "upsert": "true"},
                )
        else:
            with open(temp_file_path, "rb") as f:
                response = supabase.storage.from_("test_bucket").upload(
                    path=file_path,  # Save file with email identifier
                    file=f,
                    file_options={"cache-control": "3600", "upsert": "true"},
                )

        default_storage.delete(temp_file_path)
        # Check for errors in the upload/update response
        # if response.get("error"):
        #     return JsonResponse({"error": response["error"]["message"]}, status=500)

        # Get the public URL of the uploaded/updated file
        public_url_response = supabase.storage.from_("test_bucket").get_public_url(file_path)
        
        print(public_url_response)

        if not public_url_response:
            return JsonResponse({"error": "Failed to retrieve public URL"}, status=500)

        return JsonResponse({"url": public_url_response}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)
    
@csrf_exempt
def get_website_details_by_url(request, slug):
    try:
        # Retrieve the user data using the email
        user_url = "http://localhost:5000/" + slug
        response = supabase.table("user_data").select("*").eq('url', user_url).execute()
        data_to_return = response.data[0]['data']
        return JsonResponse({"content": data_to_return, "url_hidden": response.data[0]['url_hidden']}, status=200)

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
    print(response)
    if response.data[0]['data'] is None:
        return JsonResponse({"content": {}}, status=200)
    return JsonResponse({"content": response.data[0]['data'], "subscription_status":response.data[0]['subscription_status']}, status=200)

    
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

        # Step 3: Create a Stripe Customer
        stripe_customer = stripe.Customer.create(email=email, metadata={"supabase_user_id": user_id})

        #Step 4: Initial User Data
        insert_response = supabase.table('user_data').insert({
            'id': user_id,  # Use the UUID from authentication
            'email': email,  # Optional: Store email if needed
            'data': None,  # Leave other columns empty or set to None
            'url': None,  # You can leave 'url' blank for now as well
            'url_hidden': True,
            'stripe_customer_id': stripe_customer['id'],  # Store Stripe customer ID
            'subscription_status': 'inactive',  # Default status
        }).execute()

        # Step 5: Return the response with user information
        return JsonResponse(
            {
                "message": "User created successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                    "stripe_customer_id": stripe_customer['id'],
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
        response = supabase.table("user_data").select("*").eq('email', email).execute()
        stripe_id = response.data[0]['stripe_customer_id']
        print(stripe_id)
        return JsonResponse(
            {
                "message": "User logged in successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                    "stripe_customer_id": stripe_id
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

@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        stripe_customer_id = data.get("stripe_customer_id")
        price_id = "price_1QOdku00k5Gv8VrIJhm4YPyE"  # Use the ID of your subscription price in Stripe

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url="http://localhost:5000/home?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:5000/login",
                customer=stripe_customer_id,
            )
            return JsonResponse({"url": session.url}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    endpoint_secret = settings.STRIPE_WEBHOOK_LOCAL_KEY

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle the event
    if event["type"] == "invoice.payment_succeeded":
        subscription = event["data"]["object"]["subscription"]
        customer_id = event["data"]["object"]["customer"]

        # Update Supabase subscription status to 'active'
        supabase.table("user_data").update({"subscription_status": "active", "url_hidden":False}).eq("stripe_customer_id", customer_id).execute()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        # Update Supabase subscription status to 'inactive'
        supabase.table("user_data").update({"subscription_status": "inactive", "url_hidden":True}).eq("stripe_customer_id", customer_id).execute()

    return JsonResponse({"status": "success"}, status=200)

#this will be needed later
def require_active_subscription(func):
    def wrapper(request, *args, **kwargs):
        user_id = request.headers.get("X-User-Id")  # Assume you pass the Supabase user ID in the header
        response = supabase.table("user_data").select("subscription_status").eq("id", user_id).single().execute()

        if response.get("data", {}).get("subscription_status") != "active":
            return JsonResponse({"error": "Subscription required"}, status=403)

        return func(request, *args, **kwargs)
    return wrapper


@require_active_subscription
def protected_view(request):
    return JsonResponse({"message": "Welcome to the subscription-only area!"})

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