import math
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from secret import firebase_key,getDBKey
from user import User
from match import Match

class firebaseDB():
    def __init__(self):
        cred = credentials.Certificate(firebase_key()[0])
        firebase_admin.initialize_app(cred, {
            "projectId": firebase_key()[1],
        })

        self.db = firestore.client()
        self.key = getDBKey()

    def getAllUser(self):
        allUser = {}
        docr_ref = self.db.collection(self.key["u"]).stream()
        for doc in docr_ref:
            allUser[doc.id] = User.from_dict(doc.to_dict())
        return allUser
    
    def getAllMatch(self):
        allMatch = {}
        docr_ref = self.db.collection(self.key["m"]).stream()
        for doc in docr_ref:
            allMatch[doc.id] = Match.from_dict(doc.to_dict())
        return allMatch
    
    def isMatchExist(self,matchId):
        doc_ref = self.db.collection(self.key["m"]).document(matchId)

        doc = doc_ref.get()
        if doc.exists:
            return True
        else:
            return False

    #{puuid: User}, [puuid], match, {puuid: UserMatch}
    def putData(self,userDict,match,userMatch):
        if self.isMatchExist(match[0]):
            return False
        
        for k,v in userDict.items():
            self.db.collection(self.key["u"]).document(k).set(v.to_dict())
        self.db.collection(self.key["m"]).document(match[0]).set(match[1].to_dict())

        for k,v in userMatch.items():
            self.db.collection(self.key["u"]).document(k).collection(self.key["um"]).document(match[0]).set(v.to_dict())

        return True