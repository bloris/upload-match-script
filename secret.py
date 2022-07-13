import json

def api_key():
    with open("secret.json") as f:
        json_p = json.loads(f.read())
    return json_p["api_key"]

def firebase_key():
    with open("secret.json") as f:
        json_p = json.loads(f.read())
    return json_p["firebase"],json_p["project_name"]

def get_changed_name():
    with open("secret.json") as f:
        json_p = json.loads(f.read())
    return json_p["changed_name"]