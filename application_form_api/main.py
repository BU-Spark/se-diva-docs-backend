from fastapi import FastAPI, UploadFile, File
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import Applicant
import mongo_test
from fastapi.responses import Response
from starlette_validation_uploadfile import ValidateUploadFileMiddleware

app = FastAPI()
router = APIRouter()
app.add_middleware(
        ValidateUploadFileMiddleware,
        app_path="/applicants/resume/upload",
        max_size=31457280, #30 Megabytes max upload
        file_type=["application/pdf"]
)

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