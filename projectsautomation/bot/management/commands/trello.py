import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


trello_key = os.getenv('TRELLO_KEY')
trello_token = os.getenv('TRELLO_TOKEN')



def create_organization(project_name, project_start_date, project_end_date):
    url = "https://api.trello.com/1/organizations"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'displayName': f'Проект {project_name} [{project_start_date}-{project_end_date}]',
        'key': trello_key,
        'token': trello_token
    }
    response = requests.post(url, headers=headers, params=query)

def get_organization():
    url = 'https://api.trello.com/1/members/me/organizations'

    query = {
        'key': trello_key,
        'token': trello_token
    }

    response = requests.get(url, params=query)
    return response.json()
def create_board(name, project_name):
    url = "https://api.trello.com/1/boards/"

    query = {
        'idOrganization': f'{project_name}',
        'name': f'{name}',
        'key': trello_key,
        'token': trello_token
    }
    response = requests.post(url, params=query)


def get_boards_id(project_name):
    url = f"https://api.trello.com/1/organizations/{project_name}/boards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': trello_key,
        'token': trello_token
    }

    response = requests.get(url, headers=headers, params=query)
    return response.json()

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))


def add_member(board_id, member, email):
    url = f'https://api.trello.com/1/boards/{board_id}/members'
    headers = {
        "Content-Type": "application/json"
    }
    query = {
        # Valid values: admin, normal, observer
        'email': email,
        'type': 'normal',
        'key': trello_key,
        'token': trello_token
    }
    payload = json.dumps({
        "fullName": member
    })

    response = requests.put(url, data=payload, headers=headers, params=query)