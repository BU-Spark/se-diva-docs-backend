from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from models import Applicant
import mongo_test
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
import stripe
import pymongo
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from passlib.pwd import genword

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# generate a new password hash
def generate_password(password: str):
    return pwd_context.hash(password)

# generate a random password
def generate_random_password(length=12):
    return genword(length=length)  # Directly call genword from passlib.pwd

password = generate_random_password()

print(type(password))
print(password)
print(str(password))
