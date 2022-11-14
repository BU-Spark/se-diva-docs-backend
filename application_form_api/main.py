from typing import List
from fastapi import FastAPI
from models import Applicant
import mongo_test


app = FastAPI()

db: List[Applicant] = []

@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    # db.append(applicant)
    mongo_test.write_to_mongo(applicant.dict(), 'ApplicationForm', 'SubmittedApplications')
    return applicant

@app.get("/applicants/view")
def view_applicants():
    return db
