import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from secret import firebase_key

def dbInit():
    cred = credentials.Certificate(firebase_key()[0])
    firebase_admin.initialize_app(cred, {
        "projectId": firebase_key()[1],
    })

    db = firestore.client()
    return db
