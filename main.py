from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from models import Applicant
import db_functions
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
from dotenv import load_dotenv

load_dotenv()

# Set your Stripe API key and webhook signing secret
stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"
webhook_secret = "whsec_2TUuXZRoJH0zhuBxn5HYG1ClhX9XPpbM"

# This is the secret key used to sign JWT tokens. Replace it with a secret of your own.
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
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

app = FastAPI(
    title="DivaDocs API",
    description="DivaDocs Backend API",
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

@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    # db.append(applicant)
    db_functions.write_to_mongo(applicant.dict(), 'ApplicationForm', 'SubmittedApplications')
    return applicant


@app.get("/applicants/view")
def view_applicants(response: Response):
    applicants = db_functions.read_from_mongo('ApplicationForm', 'SubmittedApplications')
    response = JSONResponse(content=applicants)
    response.headers["X-Total-Count"] = str(len(applicants))
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return response

@app.get("/applicants/view/{id}")
def view_applicant(id: str, response: Response):
    applicants = db_functions.read_from_mongo('ApplicationForm', 'SubmittedApplications')
    applicant = next((a for a in applicants if a.get('id') == id), None)
    if not applicant:
        return JSONResponse(content={'error': 'Applicant not found'}, status_code=404)

    response = JSONResponse(content=applicant)
    return response

@app.get("/approvedapplicants/view")
def view_approved_applicants():
    all_applicants = db_functions.get_all_approved()
    return JSONResponse(content=all_applicants, status_code=200)


@app.post("/applicants/resume/upload")
async def upload_file(upload_file: UploadFile = File(...)):
    if upload_file.content_type != "application/pdf":
        return JSONResponse(content={"error": "invalid file type. Only PDF accepted", "upload_status":"data upload not successful"}, status_code=422)
    with open(upload_file.filename, 'wb') as image:
        content = await upload_file.read()
        image.write(content)
        image.close()
        db_functions.upload_file_to_mongo('ApplicationForm', 'SubmittedApplications', content, upload_file.filename)
    return JSONResponse(content={"filename": upload_file.filename, "upload_status":"data uploaded success"}, status_code=200)


@app.get("/applicants/downloadresume/{name_file}")
def download_file(name_file: str):
    fileFromDB = db_functions.download_file_from_mongo('ApplicationForm', name_file)
    return Response(fileFromDB, media_type='application/pdf')


@app.post("/applicants/approveapplicant")
def requestpayment(applicant: Applicant):
    applicant_dict = applicant.dict()
    return db_functions.send_payment(applicant_dict["id"], applicant_dict["applicant_status"]["subscription_tier"])


@app.post('/webhook')
async def handle_webhook(request: Request):
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
        client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
        db = client['ApplicationForm']
        target_collection = db['ApprovedApplications']

        # Update document
        query = {"id": str(universal_applicant_id)}
        new_values = {"$set": {"applicant_status.paid": True, "applicant_status.stripe_customer_id": str(customer_id), "applicant_status.approved": True, "applicant_status.account_password": str(hashed_password)}}
        target_collection.update_one(query, new_values)
        db_functions.send_login_email(universal_applicant_id, password)

    # Return a 200 response to acknowledge receipt of the event
    return JSONResponse(content={'test': True})


def authenticate_user(username: str, password: str):
    user = db_functions.get_password(username)
    if not user:
        return False
    hashed_password = user["applicant_status"]["account_password"]
    if verify_password(password, hashed_password) == False:
        return False
    return user

def authenticate_admin_user(username: str, password: str):
    user = db_functions.get_password_admin(username)
    if not user:
        return False
    hashed_password = user["password"]
    print(username + " " + password + " " + hashed_password)
    if not hashed_password == password:
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["primary_email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/admin_login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_admin_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected_endpoint")
async def protected_endpoint(token: str = Depends(oauth2_scheme)):
    # authenticate the user based on the token
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"SUCCESS": "YOU HAVE LOGGED IN!"}

@app.post("/forgot_password")
def forgot_password(username: str):
    password = generate_random_password()
    hashed_password = generate_password(password)
    return db_functions.send_forgotPassword_email(username, password, hashed_password)

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        # query the database to get the user by username
        user = db_functions.get_user_by_username(username)
        return user
    except Exception as e:
        return e

@app.post("/applicants/declineapplicant")
def decline_applicant(applicant: Applicant):
    applicant_dict = applicant.dict()
    return db_functions.applicant_denied(applicant_dict["id"])

@app.get("/membershipapplicants/view")
def membershipapplicants_view():
    all_applicants = db_functions.pull_approved_applicants()
    return JSONResponse(content=all_applicants, status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
