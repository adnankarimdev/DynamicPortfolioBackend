prompt_resume_creator = """
I will be giving you a resume/cv. Everything should be in first person for where it's relevant. 
Note: Certifications does not imply awards. They are two different things. For example, scholarships and grants fall under awards.
You must not take any shortcuts or skip any details present in the CV unless it does not match the format below. Your goal is to extract the information and put it into this exact format:

{
  "name": "Hi, I'm <first_name> 👋",
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
      "id": <randomly_genarated_32_int_number>
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
  "projectsWebsiteHeader":<Engaging website title for projects section based on projects in resume; make it catchy>,
  "projectsWebsiteSubtitle":<Engaging website description for projects section based on projects in resume; make it catchy>
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
  "hackathonWebsiteHeader":<Engaging website title for projects section based on projects in resume; make it catchy. Leave empty if nothing in hackathon>,
  "hackathonWebsiteSubtitle":<Engaging website description for projects section based on projects in resume; make it catchy. Leave empty if nothing in hackathon>
  "papers": [
    {
      "title": "",
      "coAuthors": [],
      "publicationDate": "",
      "conference": "",
      "journal": "",
      "doi": "",
      "abstract": "",
      "link": "",
    }
  ],
  "papersWebsiteHeader":<Engaging website title for papers section>,
  "papersWebsiteSubtitle":<Engaging website description for papers section>
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

Fill in the fields with appropriate information. You should also generate the description and summary field based on the resume/cv. Return ONLY the JSON object with no additional text or formatting. All string values must be wrapped in double quotes. For all logos, like logoUrl, use this format:  https://logo.clearbit.com/<full_company_name>.com. 
Ensure the response can be parsed by json.loads() in Python.
Note: for coAuthors, also include the name of the person who submitted this resume. Awards can be grants too. Please use your reasoning to figure out what should be included in the awards section. Finally, make sure anything in the same section that has dates is ordered from most recent (first) to earliest (last)



NOTE: Ensure the response can be parsed by json.loads() in Python. 	Please provide the data inside plain brackets, without using the ```json or any code block formatting. Do not include syntax for code formatting; just return the data in plain text.
"""