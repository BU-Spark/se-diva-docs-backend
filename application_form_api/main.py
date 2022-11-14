from typing import List
from fastapi import FastAPI
from models import Applicant

app = FastAPI()

db: List[Applicant] = []

@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    db.append(applicant)
    return applicant

@app.get("/applicants/view")
def view_applicants():
    return db;