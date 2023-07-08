from .drivers.crypt import get_password_hash, verify_password, create_access_token, decode_access_token
from .schemas import UserInsert, UserBASE, Login
from datetime import datetime
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from .drivers.envd import get_env, init
from os.path import join
import redis

r = redis.Redis(
    host='redis-10652.c292.ap-southeast-1-1.ec2.cloud.redislabs.com',
    port=10652,
    password=get_env("REDIS_PASSWD"))

mongodb_client = MongoClient(get_env("MONGO_DB_URL"),tls=True,tlsCertificateKeyFile=join(init(),"mongodb.pem"),server_api=ServerApi('1'))
mongodb_db = mongodb_client["mStudents"]
mongodb_acc = mongodb_db["accounts"]

def authenticate_user(login: Login):
    user = mongodb_acc.find_one({"email":login.email})
    if not user:
        return {"success":False, "reason":"User doesnt exist"}
    user = dict(user)
    if user["activated"]:
        if not verify_password(login.password, user["hashed_password"]):
            return {"success":False}
        return {"success":True, "result":create_access_token({"sub":login.email})}
    return {"success":False, "reason":"Account not activated"}

def insert_user(user: UserInsert):
    user_dict = user.dict(exclude={"password"})
    user_dict["created_on"] = datetime.today().replace(microsecond=0)
    user_dict["hashed_password"] = get_password_hash(user.password)
    user_dict["activated"] = False
    try:
        mongodb_acc.insert_one(user_dict)
        r.set(user.handle, 1)
        return {"success":True, "email":user.email}
    except DuplicateKeyError as e:
        if "handle_1" in (e:=str(e)):
            return {"success":False, "reason":"The handle is already taken"}
        if "email_1" in e:
            return {"success":False, "reason":"An account already exists with the same email"}
    
def edit_user(token: str, user: UserBASE):
    email = decode_access_token(token)
    if not (a := mongodb_acc.find_one({"email":email})):
        return {"success":False, "reason":"User does not exist"}
    if a := dict(a)["activated"]:
        try: 
            mongodb_acc.update_one({"email":email}, {"$set":user.dict()})
            if a["handle"] != user.handle:
                r.delete(a)
                r.set(user.handle, 1)
            return {"success":True}
        except DuplicateKeyError as e:
            if "handle_1" in (e:=str(e)):
                return {"success":False, "reason":"The handle is already taken"}
            if "email_1" in e:
                return {"success":False, "reason":"An account already exists with the same email"}
    return {"success":False, "reason":"Account not activated"}
    
def delete_user(token: str):
    email = decode_access_token(token)
    if not (a := mongodb_acc.find_one({"email":email})):
        return {"success":False, "reason":"Account not activated"}
    if a := dict(a)["activated"]:
        if mongodb_acc.delete_one({"email":email}):
            r.delete(a["handle"])
            return {"success":True}
    return {"success":False, "reason":"Account not activated"}
    
def check_handle_availability(user_id: str):
    return not r.get(user_id)

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = mongodb_acc.find_one({"email":decode_access_token(token)})
    if not user:
        raise credentials_exception
    user = dict(user)
    if user["activated"]:
        user.pop('hashed_password')
        user["_id"] = str(user["_id"])
        return {"success":True, "result":user}
    return {"success":False, "reason":"Account not activated"}

