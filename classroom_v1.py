import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from pprint import pprint

# These scopes are only initialized when token.json is created
# To refresh, delete token.json and retry with different scopes
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses', 
    'https://www.googleapis.com/auth/classroom.announcements',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials',
    'https://www.googleapis.com/auth/classroom.topics'
]

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)
        with open('token.json', 'w') as token: token.write(creds.to_json())

    return creds

def list_courses(creds):
    try:
        service = build('classroom', 'v1', credentials = creds)

        results = service.courses().list(pageSize = 10).execute()
        courses = results.get('courses', [])

        return (courses if courses else None)           # A dictionary including the course's "id" and "name"

    except HttpError as error: print('An error occurred: %s' % error)

def list_announcements(creds, course_id):
    try:
        service = build('classroom', 'v1', credentials = creds)

        results = service.courses().announcements().list(courseId = course_id, pageSize = 10).execute()
        announcements = results.get('announcements', [])

        return (announcements if announcements else None) # A dictionary including the announcement's "courseId", "id" and "text"

    except HttpError as error: print('An error occurred: %s' % error)

def create_announcement(creds, course_id, body):
    try: 
        service = build('classroom', 'v1', credentials = creds)
        results = service.courses().announcements().create(courseId = course_id, body = { 'text': body }).execute()
        return results

    except HttpError as error: print('An error occurred: %s' % error)

def create_assignment(creds, course_id, title, descr, due_date):
    # Checks
    assert due_date >= datetime.now()

    try: 
        service = build('classroom', 'v1', credentials = creds)
        results = service.courses().courseWork().create(courseId = course_id, body = {
            'title': title,
            'description': descr,
            'dueDate': {
                'day': due_date.day,
                'month': due_date.month,
                'year': due_date.year
            },
            'dueTime': {
                'hours': 10 # FOr some reason 10 is 7pm
            },
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED'
        }).execute()
        return results

    except HttpError as error: print('An error occurred: %s' % error)

if __name__ == '__main__':
    creds = authenticate()
    course_id = '504713357003' # For the self-study classroom

    due_date = datetime.fromisoformat('2023-01-02')

    res = create_assignment(creds, course_id = course_id, title = 'Dummy assignment', descr = 'Dummy text', due_date = due_date)
    print(res)
