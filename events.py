import requests
from datetime import datetime, timedelta
import configparser
import os

def get_start_of_week(weeks_ago=0):
    now = datetime.utcnow()
    start_of_week = now - timedelta(days=now.weekday()+1, weeks=weeks_ago)
    return start_of_week

def read_config():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = configparser.ConfigParser()
    config.read(os.path.join(__location__, 'conf.ini'))
    return config

# main program
if __name__ == "__main__":

    config = read_config()
    print("config {}", config)

    # Replace '<YOUR-TOKEN>' with your actual GitHub token and 'USERNAME' with the GitHub username
    your_token = config['Settings']['token']
    print("your_token", your_token)
    username = config['Settings']['username']
    print("username", username)

    url = f"https://api.github.com/users/{username}/events"

    # Set up the headers as per the curl command
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {your_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Make the request to GitHub with headers
    response = requests.get(url, headers=headers)
    events = response.json()  # Convert the response to JSON

    # Calculate the date one week ago from today
    #one_week_ago = datetime.utcnow() - timedelta(days=7)
    one_week_ago = get_start_of_week(1)

    # Filter events that were created in the last week
    recent_events = [event for event in events if datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ") > one_week_ago]

    # Define a dictionary to map English weekday names to Finnish ones
    weekday_map = {
        'Monday': 'Maanantai',
        'Tuesday': 'Tiistai',
        'Wednesday': 'Keskiviikko',
        'Thursday': 'Torstai',
        'Friday': 'Perjantai',
        'Saturday': 'Lauantai',
        'Sunday': 'Sunnuntai'
    }

    # Generate a simple list of events
    simple_events_list = [{
        'type': event['type'],
        'repo': event['repo']['name'],
        'created_at': datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
        'message': event['payload']['commits'][0]['message'] if event['type'] == 'PushEvent' else "",
        'ref_type': event['payload']['ref_type'] if event['type'] == 'CreateEvent' else "",
        'ref': event['payload']['ref'] if event['type'] == 'CreateEvent' else "",
        'tag_name': event['payload']['release']['tag_name'] if event['type'] == 'ReleaseEvent' else ""
    } for event in recent_events]


    # Convert 'created_at' to Finnish format
    for event in simple_events_list:
        dt = event['created_at']
        dt += timedelta(hours=2)
        finnish_date = f"{dt.day}.{dt.month}.{dt.year} {dt.hour}:{dt.minute}:{dt.second} {weekday_map[dt.strftime('%A')]} "
        event['created_at'] = finnish_date

    # Calculate maximum length of data in each column
    max_lengths = {
        'type': max(len(x['type']) for x in simple_events_list),
        'repo': max(len(x['repo']) for x in simple_events_list),
        'created_at': max(len(x['created_at']) for x in simple_events_list),
        'message': max(len(str(x['message'])) for x in simple_events_list),
        'ref_type': max(len(str(x['ref_type'])) for x in simple_events_list),
        'ref': max(len(str(x['ref'])) for x in simple_events_list),
        'tag_name': max(len(str(x['tag_name'])) for x in simple_events_list),
    }

    # Print the headers
    print("{:<{}} {:<{}} {:<{}} {:<{}} {:<{}} {:<{}} {:<{}}".format(
        "Event Type", max_lengths['type'],
        "Repo", max_lengths['repo'],
        "Created At", max_lengths['created_at'],
        "Message", max_lengths['message'],
        "Ref Type", max_lengths['ref_type'],
        "Ref", max_lengths['ref'],
        "Tag Name", max_lengths['tag_name']
    ))


    # Sort the events by 'created_at'
    simple_events_list = sorted(simple_events_list, key=lambda x: x['created_at'])

    # Initialize the previous date to None
    prev_date = None

    # Print the simple list of events
    for event in simple_events_list:
        # If the date has changed, print an empty row or a separator
        # Convert 'created_at' to a datetime object
        #created_at = datetime.strptime(event['created_at'], '%A %d.%m.%Y %H:%M:%S')

        # If the date has changed, print an empty row or a separator
        #if prev_date is not None and created_at.date() != prev_date:
        #    print("------ {} ------".format(prev_date.strftime('%A %d.%m.%Y')))



        print("{:<{}} {:<{}} {:<{}} {:<{}} {:<{}} {:<{}} {:<{}}".format(
            event['type'], max_lengths['type'],
            event['repo'], max_lengths['repo'],
            event['created_at'], max_lengths['created_at'],
            str(event['message']) if event['message'] else '', max_lengths['message'],
            str(event['ref_type']) if event['ref_type'] else '', max_lengths['ref_type'],
            str(event['ref']) if event['ref'] else '', max_lengths['ref'],
            str(event['tag_name']) if event['tag_name'] else '', max_lengths['tag_name']
        ))

        # Update the previous date
        #prev_date = created_at.date()