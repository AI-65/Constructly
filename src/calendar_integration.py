from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from googleapiclient.errors import HttpError
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# The scope tells Google what kind of access you need to the user's data
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    token_path = 'token.json'  # Path to the token file

    # Check if the token file exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service



def create_event(start_time_str, summary, duration=1, description=None, location=None):
    service = get_calendar_service()

    start_time = datetime.datetime.fromisoformat(start_time_str)
    end_time = start_time + datetime.timedelta(hours=duration)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Berlin',  # Replace with your time zone
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Berlin',  # Replace with your time zone
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (created_event.get('htmlLink')))
        return created_event
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_events_on_date(date_str):
    service = get_calendar_service()
    date = datetime.datetime.fromisoformat(date_str).date()
    start_time = datetime.datetime.combine(date, datetime.datetime.min.time()).isoformat() + 'Z'
    end_time = datetime.datetime.combine(date, datetime.datetime.max.time()).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=start_time,
                                          timeMax=end_time, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])



