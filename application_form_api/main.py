from fastapi import FastAPI, UploadFile, File
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import Applicant
import mongo_test
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
import stripe
import pymongo

# Set your Stripe API key and webhook signing secret
stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"
webhook_secret = "whsec_2TUuXZRoJH0zhuBxn5HYG1ClhX9XPpbM"

app = FastAPI()
router = APIRouter()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

subscription_tier_list = {
    "student": 100,
    "premed": 200,
    "doctor": 300
}


@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    # db.append(applicant)
    mongo_test.write_to_mongo(applicant.dict(), 'ApplicationForm', 'SubmittedApplications')
    return applicant


@app.get("/applicants/view")
def view_applicants():
    return mongo_test.read_from_mongo('ApplicationForm', 'SubmittedApplications')

@app.get("/approvedapplicants/view")
def view_approved_applicants():
    return mongo_test.get_all_approved()


@app.post("/applicants/resume/upload")
async def upload_file(upload_file: UploadFile = File(...)):
    if upload_file.content_type != "application/pdf":
        return JSONResponse(content={"error": "invalid file type. Only PDF accepted", "upload_status":"data upload not successful"}, status_code=422)
    with open(upload_file.filename, 'wb') as image:
        content = await upload_file.read()
        image.write(content)
        image.close()
        mongo_test.upload_file_to_mongo('ApplicationForm', 'SubmittedApplications', content, upload_file.filename)
    return JSONResponse(content={"filename": upload_file.filename, "upload_status":"data uploaded success"}, status_code=200)


@app.get("/applicants/downloadresume/{name_file}")
def download_file(name_file: str):
    fileFromDB = mongo_test.download_file_from_mongo('ApplicationForm', name_file)
    return Response(fileFromDB, media_type='application/pdf')


@app.post("/applicants/approveapplicant")
def requestpayment(applicant: Applicant):
    applicant_dict = applicant.dict()
    return mongo_test.send_payment(applicant_dict["id"])


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
        print("id: " + universal_applicant_id)
        print("customer_id: " + customer_id)
        return JSONResponse(content={'customer_id': customer_id})

    # Mongo: Change applicant paid -> true, attach customer id to applicant
    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
    db = client['ApplicationForm']
    target_collection = db['ApprovedApplications']

    # Update document
    query = {"id": str(universal_applicant_id)}
    new_values = {"$set": {"paid": True, "stripe_customer_id": str(customer_id), "approved": True}}
    target_collection.update_one(query, new_values)

    # Return a 200 response to acknowledge receipt of the event
    return JSONResponse(content={'test': True})
