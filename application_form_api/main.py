from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import Applicant
import mongo_test
from os import getcwd
from fastapi.responses import FileResponse


app = FastAPI()
router = APIRouter()
db: List[Applicant] = []

@app.post("/applicants/add")
def store_applicants(applicant: Applicant):
    # db.append(applicant)
    mongo_test.write_to_mongo(applicant.dict(), 'ApplicationForm', 'SubmittedApplications')
    return applicant

@app.get("/applicants/view")
def view_applicants():
    return mongo_test.read_from_mongo('ApplicationForm', 'SubmittedApplications') # For now, SubmittedApplications

@app.post("/applicants/resume/upload")
async def upload_file(file: UploadFile = File(...)):
    mongo_test.upload_file_to_mongo('ApplicationForm', 'SubmittedApplications', file, file.filename)
    return JSONResponse(content={"filename": file.filename}, status_code=200)

@app.get("/applicants/downloadresume/{name_file}")
def download_file(name_file: str):
    resumelist = mongo_test.read_from_mongo('ApplicationForm', 'SubmittedApplications')
    return FileResponse(path=getcwd() + "/" + name_file, media_type='application/octet-stream', filename=name_file)