import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


trello_key = os.getenv('TRELLO_KEY')
trello_token = os.getenv('TRELLO_TOKEN')
def create_board(name):
    url = "https://api.trello.com/1/boards/"

    query = {
        'name': f'{name}',
        'key': trello_key,
        'token': trello_token
    }
    response = requests.post(url, params=query)


def get_board_id(board_name):
    url = f'https://api.trello.com/1/members/me/boards'
    query = {
        'key': trello_key,
        'token': trello_token
    }
    response = requests.get(url, params=query)
    boards = response.json()
    board_id = None
    for board in boards:
        if board['name'] == board_name:
            board_id = board['id']
            break

    return board_id


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