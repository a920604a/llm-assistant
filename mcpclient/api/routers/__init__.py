import firebase_admin
from config import settings
from firebase_admin import credentials

cred = credentials.Certificate(f"{settings.FIRBASE_KEY_PATH}/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
