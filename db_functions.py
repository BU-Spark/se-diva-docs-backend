import pymongo
import gridfs
import smtplib
import random
from email.mime.text import MIMEText
import stripe
from email.mime.multipart import MIMEMultipart
from fastapi.responses import JSONResponse
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


def write_to_mongo(document, database, collection, client):
    """
    Write a document to a MongoDB database and collection.

    Args:
        document (dict): The document to write.
        database (str): The name of the database.
        collection (str): The name of the collection.

    Returns:
        None
    """
    # Select database
    mydb = client[database]

    # Select collection
    mycol = mydb[collection]

    # Write to the collection in the database
    x = mycol.insert_one(document)

def read_from_mongo(database, collection, client):
    """
    Read all documents from a MongoDB collection.

    Args:
        database (str): The name of the database.
        collection (str): The name of the collection.

    Returns:
        list: A list of all documents in the collection.
    """
    
    # Select database
    mydb = client[database]

    # Select collection
    mycol = mydb[collection]

    # Read from the collection in the database and append to output list
    output_list = []
    for x in mycol.find({}, {"_id": 0}):
        output_list.append(x)

    return output_list

def upload_file_to_mongo(database, collection, file, file_name, client):
    """
    Upload a file to a MongoDB database and collection.

    Args:
        database (str): The name of the database.
        collection (str): The name of the collection.
        file (bytes): The file to upload.
        file_name (str): The name of the file.

    Returns:
        None
    """
    # Select database
    mydb = client[database]

    # Select collection
    mycol = mydb[collection]

    # Upload the file
    fs = gridfs.GridFS(mydb)
    fs.put(file, filename=file_name)

def download_file_from_mongo(database, file_name, client):

    # Establish Connection to MongoDB

    mydb = client[database]

    fs = gridfs.GridFS(mydb)

    data = mydb.fs.files.find_one({'filename' : file_name})

    my_id = data['_id']

    outputdata = fs.get(my_id).read()

    return outputdata

def send_payment(u_id, subscription_tier, client):

    if len(subscription_tier) == 0:
        return JSONResponse(content={'error': 'Subscription Tier Not Assigned'}, status_code=400)

    # Get the ID

    id = u_id  # Change to U_ID in production

    # Connect to MongoDB

    try:
        db = client['ApplicationForm']
        source_collection = db['SubmittedApplications']
        target_collection = db['ApprovedApplications']
    except Exception as e:
        return JSONResponse(content={'error':'mongo connection error'}, status_code=400)

    # Find the document with "id" field equals to U_ID

    document1 = source_collection.find_one({"id": id})

    query = {"id": document1['id']}
    new_values = {"$set": {"applicant_status.subscription_tier": str(subscription_tier)}}
    source_collection.update_one(query, new_values)

    applicant_email = document1['primary_email']

    # Move the Applicant to Approved Applications

    document = source_collection.find_one({"id": id})

    target_collection.insert_one(document)

    # Delete the Applicant from Submitted Applications

    source_collection.delete_one({'id': id})

    # Close the MongoDB connection

    client.close()

    # Set your API key ---

    stripe.api_key = os.getenv("stripe_api_key")

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

    to_email = applicant_email
   
    # Send the email
    try:
    # Send the email
        send_email_with_template(to_email, document['first_name'], "d-e4a2d364df9b4cfdba541a87462b8cae", payment_link['url'])
    except Exception as e:
        # Return error message if email not sent successfully
        return {'error': 'email not sent'}

    return JSONResponse(content={'success': 'Email sent'}, status_code=200)

def get_all_approved(client):
        
    db = client['ApplicationForm']
    
    target_collection = db['ApprovedApplications']
    
    # Print all documents in collection
    output_list = []

    for x in target_collection.find({}, {"_id": 0}):
        output_list.append(x)

    return output_list

def get_password(email, client):
    
    # connect to the MongoDB client
       
    db = client['ApplicationForm']
    
    approved_applicants = db['ApprovedApplications']
    
    # search for the applicant with the given email
    try:
        applicant = approved_applicants.find_one({'primary_email': email})
    except Exception as e:
        return JSONResponse(content={'failure': 'applicant not found'}, status_code=400)

    return applicant

def applicant_denied(u_id, client):
    
    # Get the ID

    id = u_id # Change to U_ID in production

    # Connect to MongoDB

    try:
        db = client['ApplicationForm']
        source_collection = db['SubmittedApplications']
        target_collection = db['DeniedApplications']
    except Exception as e:
        return JSONResponse(content={'error':'mongo connection error'}, status_code=400)

    # Find the document with "id" field equals to U_ID
    
    document = source_collection.find_one({"id": id})

    applicant_email = document['primary_email']
    
    # Move the Applicant to Denied Applications

    target_collection.insert_one(document)

    # Delete the Applicant from Submitted Applications

    source_collection.delete_one({'id': id})

    # Close the MongoDB connection
    
    client.close()

    # Send Email ----

    to_email = applicant_email

    # Send the email

    try:
        # Send the email
        send_email_with_template(to_email, document['first_name'], "d-1f3fad49f3e547f690281db893e95e24", "")
    except Exception as e:
        # Return error message if email not sent successfully
        return {'error': 'email not sent'}

    return JSONResponse(content={'success': 'Email sent'}, status_code=200)

def pull_approved_applicants(client):
    
    # Select Database

    mydb = client['ApplicationForm']

    # Select Collection

    mycol = mydb['ApprovedApplications']

    # Print all documents in collection
    output_list = []

    for document in mycol.find({"applicant_status.paid": True}, {"_id": 0}):
        output_list.append(document)

    return output_list

def send_login_email(uid, input_password, client):
    
    try:
        db = client['ApplicationForm']
        source_collection = db['ApprovedApplications']
    except Exception as e:
        return JSONResponse(content={'error':'mongo connection error'}, status_code=400)

    # Find the document with "id" field equals to U_ID
    
    document = source_collection.find_one({"id": uid})

    try:
        applicant_email = document['primary_email']
    except Exception as e:
        return {'error': 'user email not found'}

    # Send the email
    try:
    # Send the email
        send_login_info_email(applicant_email, document['first_name'], input_password)
    except Exception as e:
        # Return error message if email not sent successfully
        return {'error': 'email not sent'}

def send_forgotPassword_email(username, input_password, hashed_password, client):
    
    try:
        db = client['ApplicationForm']
        source_collection = db['ApprovedApplications']
        applicant = source_collection.find_one({'primary_email': username})
        if applicant is None:
            return JSONResponse(content={'error':'applicant not found'}, status_code=400)
    except Exception as e:
        return JSONResponse(content={'error':'applicant not found'}, status_code=400)

    # Update document
    query = {"id": applicant['id']}
    
    new_values = {"$set": {"applicant_status.account_password": hashed_password}}
    
    source_collection.update_one(query, new_values)

    from_email = "info@blackwomenmdnetwork.com"
    
    to_email = username
    
    password = "yxqgwaxfaxizhfsq"

    try:
        # Send the email
        send_forgot_password_email(to_email, applicant['first_name'], input_password)
        return JSONResponse(content={'Success': 'Password Reset'}, status_code=200)
    except Exception as e:
        # Return error message if email not sent successfully
        return {'error': 'email not sent'}
    

def send_email_with_template(to_email, user_name, template_id, payment_link):
   
    message = Mail(
        from_email=("info@blackwomenmdnetwork.com", "Black Women MD Network"),
        to_emails=to_email,
        is_multiple=True
    )
    
    # If not payment link email
    
    if len(payment_link) == 0:
        message.dynamic_template_data = {
        "applicant_name": user_name,
    }
    else:
        message.dynamic_template_data = {
        "applicant_name": user_name,
        "payment_link": str(payment_link)
    }

    # Set the template ID you got from the SendGrid dashboard
    
    message.template_id = template_id

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_login_info_email(to_email, user_name, user_password):
    # Replace "your_sendgrid_api_key" with your actual SendGrid API key

    message = Mail(
        from_email=("info@blackwomenmdnetwork.com", "Black Women MD Network"),
        to_emails=to_email,
        is_multiple=True
    )

    # Pass your dynamic content using the substitution tags you used in your template
    
    # If not payment link email
    message.dynamic_template_data = {
    "applicant_name": user_name,
    "user_email": to_email,
    "user_password": user_password
    }

    # Set the template ID you got from the SendGrid dashboard
    message.template_id = "d-a9905f686a794214a43a8e10a45d3cc3"

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_forgot_password_email(to_email, user_name, user_password):
    # Replace "your_sendgrid_api_key" with your actual SendGrid API key

    message = Mail(
        from_email=("info@blackwomenmdnetwork.com", "Black Women MD Network"),
        to_emails=to_email,
        is_multiple=True
    )

    # Pass your dynamic content using the substitution tags you used in your template
    
    # If not payment link email
    message.dynamic_template_data = {
    "applicant_name": user_name,
    "user_email": to_email,
    "user_password": user_password
    }

    # Set the template ID you got from the SendGrid dashboard
    message.template_id = "d-d7877e6fa8a04c42bac524d06a26efef"

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_password_admin(username, client):
    db = client['AdminPortal']
    approved_applicants = db['SuperUser']
    # search for the applicant with the given email
    try:
        applicant = approved_applicants.find_one({'username': username})
    except Exception as e:
        return JSONResponse(content={'failure': 'applicant not found'}, status_code=400)

    return applicant