from django.http import HttpResponse
from django.http import HttpResponse
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

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
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