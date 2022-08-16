import json

def api_key():
    with open("secret.json", encoding = "UTF8") as f:
        json_p = json.loads(f.read())
    return json_p["api_key"]

def firebase_key():
    with open("secret.json", encoding = "UTF8") as f:
        json_p = json.loads(f.read())
    return json_p["firebase"],json_p["project_name"]

def get_changed_name():
    with open("secret.json", encoding = "UTF8") as f:
        json_p = json.loads(f.read())
    return json_p["changed_name"]

def getDBKey():
    with open("secret.json", encoding = "UTF8") as f:
        json_p = json.loads(f.read())
    return json_p["dbKey"]

def getPath():
    with open("secret.json", encoding = "UTF8") as f:
        json_p = json.loads(f.read())
    return json_p["history_path"]