import pymongo
import gridfs
import smtplib
import random
from email.mime.text import MIMEText
import stripe
import smtplib
from email.mime.multipart import MIMEMultipart
from fastapi.responses import JSONResponse

#from bson.objectid import ObjectId

def write_to_mongo(document, database, collection):
     # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    # Select Database

    mydb = client[database]

    # Select Collection

    mycol = mydb[collection]

    # WRITE to the collection in the database

    x = mycol.insert_one(document)

def read_from_mongo(database, collection):

    # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    # Select Database

    mydb = client[database]

    # Select Collection

    mycol = mydb[collection]

    # READ from the collection in the database & print

    output_list = []

    for x in mycol.find({}, {"_id": 0}):
        output_list.append(x)

    return output_list

def upload_file_to_mongo(database, collection, file, file_name):

    # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    # Select Database

    mydb = client[database]

    # Select Collection

    mycol = mydb[collection]

    fs = gridfs.GridFS(mydb)

    fs.put(file, filename = file_name)

def download_file_from_mongo(database, file_name):

    # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    mydb = client[database]

    fs = gridfs.GridFS(mydb)

    data = mydb.fs.files.find_one({'filename' : file_name})

    my_id = data['_id']

    outputdata = fs.get(my_id).read()

    return outputdata

def send_email(recipient_email):
    # Email settings
    from_email = "vinay.metlapalli@gmail.com"
    to_email = "abhinoor@bu.edu"
    password = "mttjbrfwvzxsouql"

    # Generate a 4-digit passcode
    passcode = str(random.randint(1000, 9999))

    # Compose the email message
    #message = f"Your application to the BlackWomenMDNetwork has been approved. Visit our website at: https://blackwomenmdnetwork.com/ and use this passcode when creating an account: {passcode}"
    # Compose the email message
    message = MIMEText(f"Your application to the BlackWomenMDNetwork has been approved! Visit our website at: https://blackwomenmdnetwork.com/ and use this passcode when creating an account: {passcode}")
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = 'Your BlackWomenMDNetwork Application has been Approved!'


    # Connect to the email server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, password)

    # Send the email
    server.sendmail(from_email, to_email, message.as_string())

    # Close the server connection
    server.quit()

    print("Passcode sent successfully!")

def send_payment(u_id):

    # Get the ID

    id = u_id # Change to U_ID in production

    # Connect to MongoDB

    try:
        client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
        db = client['ApplicationForm']
        source_collection = db['SubmittedApplications']
        target_collection = db['ApprovedApplications']
    except Exception as e:
        return JSONResponse(content={'error':'mongo connection error'}, status_code=400)

    # Find the document with "id" field equals to U_ID
    
    document = source_collection.find_one({"id": id})

    applicant_email = document['primary_email']
    
    # Move the Applicant to Approved Applications

    target_collection.insert_one(document)

    # Delete the Applicant from Submitted Applications

    source_collection.delete_one({'id': id})

    # Close the MongoDB connection
    
    client.close()

    # Set your API key ---
    
    stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"
    
    # Generate the Link

    Joycelyn_Elders_Society_PID = "price_1MeN0IIOQGSqv0xR4a3TP4kh"
    Barbara_Ross_Society_PID = "price_1MekfBIOQGSqv0xRJlTX6dBv"
    Alexa_Canaday_Society_PID = "price_1MekghIOQGSqv0xRC2WHmstG"
    Mae_Jemison_Society_PID = "price_1MekibIOQGSqv0xRIc1rEmRj"
    Nancy_Oriol_Society_PID = "price_1MekjsIOQGSqv0xRz7oBw3No"

    if document["applicant_status"]["subscription_tier"] == "Joycelyn Elders Society":
        payment_link = stripe.PaymentLink.create(
        line_items=[{"price": Joycelyn_Elders_Society_PID, "quantity": 1}],
        metadata={"id": id}
    )
    elif document["applicant_status"]["subscription_tier"] == "Barbara Ross Society":
        payment_link = stripe.PaymentLink.create(
        line_items=[{"price": Barbara_Ross_Society_PID, "quantity": 1}],
        metadata={"id": id}
    )
    elif document["applicant_status"]["subscription_tier"] == "Alexa Canaday Society":
        payment_link = stripe.PaymentLink.create(
        line_items=[{"price": Alexa_Canaday_Society_PID, "quantity": 1}],
        metadata={"id": id}
    )
    elif document["applicant_status"]["subscription_tier"] == "Mae Jemison Society":
        payment_link = stripe.PaymentLink.create(
        line_items=[{"price": Mae_Jemison_Society_PID, "quantity": 1}],
        metadata={"id": id}
    )
    elif document["applicant_status"]["subscription_tier"] == "Nancy Oriol Society":
        payment_link = stripe.PaymentLink.create(
        line_items=[{"price": Nancy_Oriol_Society_PID, "quantity": 1}],
        metadata={"id": id}
    )
    else:
        return JSONResponse(content={'error': 'Subscription Tier Not Assigned'}, status_code=400)

    # Send Email ----

    # Email settings
    from_email = "vinay.metlapalli@gmail.com"
    to_email = applicant_email
    password = "mttjbrfwvzxsouql"

    # Compose the email message
    message = MIMEText(f"Your application to the BlackWomenMDNetwork has been approved! Please pay your membership fee here: {str(payment_link['url'])}")    
    message['From'] = from_email
    message['To'] = applicant_email
    message['Subject'] = 'Your BlackWomenMDNetwork Application has been Approved!'

    # Connect to the email server
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
    except Exception as e:
        return JSONResponse(content={'error': 'not able to connect to email server'}, status_code=400)

    # Send the email
    try:
    # Send the email
        server.sendmail(from_email, to_email, message.as_string())
    except Exception as e:
        # Return error message if email not sent successfully
        return {'error': 'email not sent'}

    # Close the server connection
    server.quit()

    return JSONResponse(content={'success': 'Email sent'}, status_code=200)

def get_all_approved():
    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
    db = client['ApplicationForm']
    target_collection = db['ApprovedApplications']
    # Print all documents in collection

    output_list = []

    for x in target_collection.find():
        output_list.append(x)

    return output_list

def get_password(email):
    # connect to the MongoDB client
    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
    db = client['ApplicationForm']
    approved_applicants = db['ApprovedApplications']
    # search for the applicant with the given email
    applicant = approved_applicants.find_one({'primary_email': email})
    if applicant['applicant_status']['approved'] and applicant['applicant_status']['paid']:
        password = applicant['applicant_status']['account_password']
        return JSONResponse(content={'success': password}, status_code=200)
    else:
        return JSONResponse(content={'failure': 'applicant not paid/approved'}, status_code=400)
    