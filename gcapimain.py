import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
          'https://www.googleapis.com/auth/classroom.topics.readonly']


def get_info(link):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=37085)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])
    if not courses:
        return None
    for course in courses:
        if course.get('alternateLink').split("classroom.google.com/c/")[1] in link:
            cid = course.get('id')
            cwork = service.courses().courseWork().list(courseId=cid).execute().get('courseWork')
            if not cwork:
                return None
            for work in cwork:
                if link.endswith(work.get('alternateLink').split('//classroom.google.com/c/')[1].split('/a/')[1]):
                    return {
                        'course': course,
                        'work': work
                    }
