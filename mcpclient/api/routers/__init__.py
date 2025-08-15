import firebase_admin
from firebase_admin import credentials
from conf import FIRBASE_KEY_PATH

cred = credentials.Certificate(f"{FIRBASE_KEY_PATH}/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
