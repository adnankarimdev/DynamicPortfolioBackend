prompt_resume_creator = """
I will be giving you a resume/cv. Your goal is to extract the information and put it into this exact format:

{
  "name": "",
  "initials": "",
  "url": "",
  "location": "",
  "locationLink": "",
  "description": "",
  "summary": "",
  "avatarUrl": "",
  "skills": [],
  "navbar": [
    { "href": "/", "icon": "HomeIcon", "label": "Home" },
    { "href": "/blog", "icon": "NotebookIcon", "label": "Blog" }
  ],
  "contact": {
    "email": "",
    "tel": "",
    "social": {
      "GitHub": {
        "name": "GitHub",
        "url": "",
        "icon": "Icons.github",
        "navbar": true
      },
      "LinkedIn": {
        "name": "LinkedIn",
        "url": "",
        "icon": "Icons.linkedin",
        "navbar": true
      },
      "X": {
        "name": "X",
        "url": "",
        "icon": "Icons.x",
        "navbar": true
      },
      "Youtube": {
        "name": "Youtube",
        "url": "",
        "icon": "Icons.youtube",
        "navbar": true
      },
      "email": {
        "name": "Send Email",
        "url": "",
        "icon": "Icons.email",
        "navbar": false
      }
    }
  },
  "work": [
    {
      "company": "",
      "href": "",
      "badges": [],
      "location": "",
      "title": "",
      "logoUrl": "",
      "start": "",
      "end": "",
      "description": ""
    }
  ],
  "education": [
    {
      "school": "",
      "href": "",
      "degree": "",
      "logoUrl": "",
      "start": "",
      "end": ""
    }
  ],
  "projects": [
    {
      "title": "",
      "href": "",
      "dates": "",
      "active": false,
      "description": "",
      "technologies": [],
      "links": [
        {
          "type": "",
          "href": "",
          "icon": null
        }
      ],
      "image": "",
      "video": ""
    }
  ],
  "hackathons": [
    {
      "title": "",
      "dates": "",
      "location": "",
      "description": "",
      "image": "",
      "mlh": "",
      "win": "",
      "links": [
        {
          "title": "",
          "icon": null,
          "href": ""
        }
      ]
    }
  ],
  "papers": [
    {
      "title": "",
      "coAuthors": [],
      "publicationDate": "",
      "conference": "",
      "journal": "",
      "doi": "",
      "abstract": "",
      "link": ""
    }
  ],
  "certifications": [
    {
      "title": "",
      "issuingOrganization": "",
      "logoUrl": "",
      "dateIssued": "",
      "credentialId": "",
      "url": ""
    }
  ],
  "volunteerWork": [
    {
      "organization": "",
      "role": "",
      "location": "",
      "start": "",
      "end": "",
      "description": ""
    }
  ],
  "awards": [
    {
      "title": "",
      "organization": "",
      "dateAwarded": "",
      "description": ""
    }
  ],
  "languages": [
    {
      "name": "",
      "proficiency": ""
    }
  ],
  "interests": [
    {
      "name": "",
      "icon": ""
    }
  ],
  "testimonials": [
    {
      "name": "",
      "role": "",
      "quote": "",
      "organization": "",
      "avatarUrl": ""
    }
  ],
  "openSourceContributions": [
    {
      "project": "",
      "repository": "",
      "role": "",
      "description": "",
      "contributionDate": ""
    }
  ],
  "speakingEngagements": [
    {
      "title": "",
      "event": "",
      "location": "",
      "date": "",
      "slidesLink": "",
      "description": ""
    }
  ],
  "patents": [
    {
      "title": "",
      "patentId": "",
      "description": "",
      "dateFiled": "",
      "status": "",
      "url": ""
    }
  ]
}

Fill in the fields with appropriate information. You should also generate the description and summary field based on the resume/cv. Return ONLY the JSON object with no additional text or formatting. All string values must be wrapped in double quotes. For all logos, like logoUrl, use this format:  https://logo.clearbit.com/<company_name>.com
Ensure the response can be parsed by json.loads() in Python.
Note: for coAuthors, also include the name of the person who submitted this resume. Awards can be grants too. Please use your reasoning to figure out what should be included in the awards section.



NOTE: Ensure the response can be parsed by json.loads() in Python. 	Please provide the data inside plain brackets, without using the ```json or any code block formatting. Do not include syntax for code formatting; just return the data in plain text.
"""