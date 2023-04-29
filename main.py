from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from models import Applicant
import db_functions
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
import stripe
import pymongo
from pymongo import MongoClient
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from passlib.pwd import genword
from dotenv import load_dotenv
import os

app = FastAPI(
    title="BWMDN API",
    description="BWMDN Backend API",
    version="1.0.0",
    expose_headers=["X-Total-Count"],
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://blackwomenmdnetwork.com",
    "https://bwmdn-admin-2.web.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()

# Create MongoDB client and return it as a dependency
def get_mongo_client():
    client = MongoClient(os.getenv("mongo_uri"))
    return client

# Set your Stripe API key and webhook signing secret
stripe.api_key = os.getenv("stripe_api_key")
webhook_secret = os.getenv("webhook_secret")

# This is the secret key used to sign JWT tokens. Replace it with a secret of your own.
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin_login")
oauth2_scheme2 = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# generate a new password hash
def generate_password(password: str):
    return pwd_context.hash(password)

# generate a random password
def generate_random_password(length=12):
    return genword(length=length)

# check if a password matches a hash
def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)

def decode_token(token, client: MongoClient):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print("Regular User: " + username)
        # Directly query the database to get the user by username
        db = client['ApplicationForm']
        users_collection = db['ApprovedApplications']
        user = users_collection.find_one({"primary_email": username})
        if not user:
            print("USER NOT FOUND")
        return user
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Unexpected error in decode_token: {e}")
        return None

def decode_token_admin(token, client: MongoClient):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print("Admin User: " + username)

        # Directly query the database to get the user by username
        db = client['AdminPortal']
        users_collection = db['SuperUser']
        user = users_collection.find_one({"username": username})
        if not user:
            print("ADMIN: USER NOT FOUND")
        return user
    except jwt.ExpiredSignatureError:
        print("ADMIN: Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("ADMIN: Invalid token")
        return None
    except Exception as e:
        print(f"ADMIN: Unexpected error in decode_token: {e}")
        return None


def authenticate_user(username: str, password: str, client: MongoClient):
    user = db_functions.get_password(username, client)
    if not user:
        return False
    hashed_password = user["applicant_status"]["account_password"]
    if verify_password(password, hashed_password) == False:
        return False
    return user

def authenticate_admin_user(username: str, password: str, client: MongoClient):
    user = db_functions.get_password_admin(username, client)
    if not user:
        return False
    hashed_password = user["password"]
    if not hashed_password == password:
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/applicants/add")
def store_applicants(applicant: Applicant, client: MongoClient = Depends(get_mongo_client)):
    # db.append(applicant)
    db_functions.write_to_mongo(applicant.dict(), 'ApplicationForm', 'SubmittedApplications', client)
    return applicant


@app.get("/applicants/view")
def view_applicants(response: Response, client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme)):
    user = decode_token_admin(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    applicants = db_functions.read_from_mongo('ApplicationForm', 'SubmittedApplications', client)
    response = JSONResponse(content=applicants)
    response.headers["X-Total-Count"] = str(len(applicants))
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return response

@app.get("/applicants/view/{id}")
def view_applicant(id: str, response: Response, client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme)):
    user = decode_token_admin(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    applicants = db_functions.read_from_mongo('ApplicationForm', 'SubmittedApplications', client)
    applicant = next((a for a in applicants if a.get('id') == id), None)
    if not applicant:
        return JSONResponse(content={'error': 'Applicant not found'}, status_code=404)

    response = JSONResponse(content=applicant)
    return response

@app.get("/approvedapplicants/view")
def view_approved_applicants(client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme)):
    user = decode_token_admin(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    all_applicants = db_functions.get_all_approved(client)
    return JSONResponse(content=all_applicants, status_code=200)


@app.post("/applicants/resume/upload")
async def upload_file(upload_file: UploadFile = File(...), client: MongoClient = Depends(get_mongo_client)):
    if upload_file.content_type != "application/pdf":
        return JSONResponse(content={"error": "invalid file type. Only PDF accepted", "upload_status":"data upload not successful"}, status_code=422)
    with open(upload_file.filename, 'wb') as image:
        content = await upload_file.read()
        image.write(content)
        image.close()
        db_functions.upload_file_to_mongo('ApplicationForm', 'SubmittedApplications', content, upload_file.filename, client)
    return JSONResponse(content={"filename": upload_file.filename, "upload_status":"data uploaded success"}, status_code=200)


@app.get("/applicants/downloadresume/{name_file}")
def download_file(name_file: str, client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme2), token_admin: str = Depends(oauth2_scheme)):
    user = decode_token(token, client)
    admin_user = decode_token_admin(token_admin, client)
    if not user and not admin_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    fileFromDB = db_functions.download_file_from_mongo('ApplicationForm', name_file, client)
    return Response(fileFromDB, media_type='application/pdf')


@app.post("/applicants/approveapplicant")
def requestpayment(applicant: Applicant, client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme)):
    user = decode_token_admin(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    applicant_dict = applicant.dict()
    return db_functions.send_payment(applicant_dict["id"], applicant_dict["applicant_status"]["subscription_tier"], client)


@app.post('/webhook')
async def handle_webhook(request: Request, client: MongoClient = Depends(get_mongo_client)):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=401, detail=str(e))

    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        universal_applicant_id = session.metadata.id
        customer_id = session.customer
        # return JSONResponse(content={'customer_id': customer_id})

        password = generate_random_password()
        hashed_password = generate_password(password)

        # Mongo: Change applicant paid -> true, attach customer id to applicant
        db = client['ApplicationForm']
        target_collection = db['ApprovedApplications']

        # Update document
        query = {"id": str(universal_applicant_id)}
        new_values = {"$set": {"applicant_status.paid": True, "applicant_status.stripe_customer_id": str(customer_id), "applicant_status.approved": True, "applicant_status.account_password": str(hashed_password)}}
        target_collection.update_one(query, new_values)
        db_functions.send_login_email(universal_applicant_id, password, client)

    # Return a 200 response to acknowledge receipt of the event
    return JSONResponse(content={'test': True})


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), client: MongoClient = Depends(get_mongo_client)):
    user = authenticate_user(form_data.username, form_data.password, client)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["primary_email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/admin_login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), client: MongoClient = Depends(get_mongo_client)):
    user = authenticate_admin_user(form_data.username, form_data.password, client)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/forgot_password")
def forgot_password(username: str, client: MongoClient = Depends(get_mongo_client)):
    password = generate_random_password()
    hashed_password = generate_password(password)
    return db_functions.send_forgotPassword_email(username, password, hashed_password, client)

@app.post("/applicants/declineapplicant")
def decline_applicant(applicant: Applicant, client: MongoClient = Depends(get_mongo_client), token: str = Depends(oauth2_scheme)):
    user = decode_token_admin(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    applicant_dict = applicant.dict()
    return db_functions.applicant_denied(applicant_dict["id"], client)

@app.get("/membershipapplicants/view")
def membershipapplicants_view(token: str = Depends(oauth2_scheme2), client: MongoClient = Depends(get_mongo_client)):
    user = decode_token(token, client)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    all_applicants = db_functions.pull_approved_applicants(client)
    return JSONResponse(content=all_applicants, status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
