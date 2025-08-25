import firebase_admin
from config import FIRBASE_KEY_PATH
from firebase_admin import credentials

cred = credentials.Certificate(f"{FIRBASE_KEY_PATH}/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
