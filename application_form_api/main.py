from typing import List
from fastapi import FastAPI
from models import Applicant
import pymongo
from se-diva-docs-backend.application_form_api.mongodb_python_script.mongo_test import *


app = FastAPI()

db: List[Applicant] = []

@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    # db.append(applicant)
    write_to_mongo(applicant, 'ApplicationForm', 'SubmittedApplications')
    return applicant

@app.get("/applicants/view")
def view_applicants():
    return db;
