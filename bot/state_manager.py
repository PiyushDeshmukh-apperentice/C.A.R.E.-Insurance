from enum import Enum

class State(Enum):
    START = 0
    ASK_EMAIL = 1
    ASK_PASSWORD = 2
    MAIN_MENU = 3
    CLAIM_TYPE_MENU = 4
    HEALTH_CLAIM_MENU = 5
    AUTO_CLAIM_MENU = 6
    UPLOADING_HEALTH_DOCS = 7
    UPLOADING_AUTO_DOCS = 8
    ASK_POLICY_NAME = 9
    ASK_AUTO_DETAILS = 10

sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = {
            "state": State.START,
            "email": None,
            "token": None,
            "docs": {},
            "doc_index": 0,
            "claim_type": None,
            "policy_name": None,
            "auto_details": {}
        }
    return sessions[user_id]
