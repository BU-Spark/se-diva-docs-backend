import pymongo
import gridfs
import smtplib
import random
from email.mime.text import MIMEText
import stripe
import smtplib
from email.mime.multipart import MIMEMultipart
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

def create_payment(applicant_email, payment_amount):

    stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"

    stripe.Price.create(currency="usd", unit_amount=1000, product='{{PRODUCT_ID}}')

    payment_link = stripe.PaymentLink.create(
        amount=payment_amount,
        currency='usd',
        refresh_url='www.google.com',
        return_url='www.google.com',
        description='Application Fee for ' + applicant_email,
        metadata={
            'email': applicant_email
        }
    )['url']
    
    # Save payment link and applicant information in your database
    
    # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    # Select Database

    mydb = client['ApplicationForm']

    # Select Collection

    mycol = mydb['SubmittedApplications']

    # specify the document by the email field
    
    query = {"email": "user_email"}

    # specify the field you want to update and its new value
    
    set_payment_link = {"$set": {"applicant_status.payment_link": payment_link}}
    set_status = {"$set": {"applicant_status.approved": True}}

    # update the document using the update_one method
    mycol.update_one(query, set_payment_link)
    mycol.update_one(query, set_status)


    # 2. Send payment link to applicant via email
    msg = MIMEMultipart()
    msg['From'] = 'vinay.metlapalli@gmail.com'
    msg['To'] = applicant_email
    msg['Subject'] = 'Payment Required for Website Access'
    body = 'Please click on the following link to make your payment: ' + payment_link
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('vinay.metlapalli@gmail.com', 'mttjbrfwvzxsouql')
    text = msg.as_string()
    server.sendmail('vinay.metlapalli@gmail.com', applicant_email, text)
    server.quit()
