from firebase_admin import auth as firebase_auth
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, APIRouter
from firebase_admin import auth as firebase_auth
from typing import Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info(f"credentials {credentials.credentials}")
    token = credentials.credentials
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


def verify_firebase_token(authorization: Optional[str] = Header(None)) -> str:
    # logger.info(f"authorization {authorization}")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )
    id_token = authorization.split(" ")[1]
    logger.info(f"id_token {id_token}")

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        return user_id
    except Exception as e:
        logger.error(f"Firebase verify_id_token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
