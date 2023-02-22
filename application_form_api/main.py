from fastapi import FastAPI, UploadFile, File
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import Applicant
import mongo_test
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
import stripe

# Set your Stripe API key and webhook signing secret
stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"
webhook_secret = "whsec_34d1b16bc211ba244123bf9fccebf7e286632563298ca36bc186df76d5bf09b6"

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


@app.post("/applicants/requestpayment")
def requestpayment(applicant: Applicant):
    applicant_dict = applicant.dict()
    mongo_test.create_payment(applicant_dict["primary_email"], subscription_tier_list[applicant_dict["applicant_status"]["subscription_tier"]])
    return JSONResponse(content={"success": "Applicant Approved, Payment Requested"}, status_code=200)


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
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        return JSONResponse(content={'received': True})
        # Do something with the payment_intent object, e.g. mark the order as paid

    # Return a 200 response to acknowledge receipt of the event
    return JSONResponse(content={'test': True})