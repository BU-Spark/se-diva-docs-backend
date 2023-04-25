# Black Women M.D. Network Backend

The Black Women M.D. Network (BWMDN) Backend API is a FastAPI based backend application to manage applications, authentication, and file uploads for the DivaDocs platform. The project uses MongoDB to store and manage the data. There are various endpoints to handle the multitude of different functions across the website.


## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Current State](#current-state)
- [Tips for Future Developers](#tips-for-future-developers)

## Overview of Software Modules

1. `main.py`: This is the main entry point of the application. It initializes and runs the web server, defines the API endpoints, and handles the requests and responses.

2. `db_functions.py`: This module is responsible for connecting to the MongoDB database, handling database operations, and providing an interface for other modules to interact with the data.

3. `models.py`: This module contains the data models and schemas used throughout the application, including Pydantic models and Enums for input validation and serialization.

## Flow Chart
`main.py` depends on `db_functions.py` for database operations, and `db_functions.py` depends on `models.py` for data models and schemas.

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7 or higher
- MongoDB Atlas Account and Cluster
- Stripe Account
- SendGrid Account

### Environment Variables

Before running the application, you need to set up the following environment variables:

- `MONGO_URI`: The MongoDB connection URI for your MongoDB Atlas cluster
- `STRIPE_API_KEY`: Your Stripe API key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret
- `SENDGRID_KEY`: Your SendGrid email API key
- `SECRET_KEY`: A secret key to sign JWT tokens (choose a strong, unique value)

## Installation

1. Clone the repository:
```
git clone https://github.com/BU-Spark/se-diva-docs-backend.git
```

2. Navigate to the cloned directory


3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Run the FastAPI server:
```
python3 main.py
or
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```


5. Visit http://127.0.0.1:5000/docs to access the Swagger UI for API documentation and testing.

## API Endpoints

The API includes the following endpoints:

- `/applicants/add`: Add applicant form data to database
- `/applicants/view`: View all applicants
- `/applicants/view/{id}`: View a specific applicant by ID
- `/applicants/resume/upload`: Upload applicant resume (PDF)
- `/applicants/downloadresume/{name_file}`: Download applicant resume
- `/applicants/approveapplicant`: Approve and request payment from the applicant
- `/webhook`: Stripe webhook endpoint
- `/login`: Authenticate users and generate JWT tokens
- `/admin_login`: Authenticate admin users and generate JWT tokens
- `/protected_endpoint`: Example of a protected endpoint that requires JWT authentication
- `/applicants/declineapplicant`: Decline an applicant
- `/membershipapplicants/view`: View all approved applicants who have paid

db_functions.py includes the following functions:

- `write_to_mongo(document, database, collection)`:Writes a given document to a specified collection in a specified database in MongoDB. 
- `read_from_mongo(database, collection)`: This function reads all the documents from a specified collection in a specified database in MongoDB.
- `upload_file_to_mongo(database, collection, file, file_name)`: This function uploads a file to GridFS in a specified database in MongoDB.
- `download_file_from_mongo(database, file_name)`: This function downloads a file from GridFS in a specified database in MongoDB.
- `send_email(recipient_email)`: This function sends an email to a specified recipient email address using SendGrid.
- `send_payment(u_id)`: Sends a Stripe payment link to the email address of the applicant whose document was moved from Submitted to Approved DB.
- `get_all_approved()`: This function retrieves all approved application forms.
- `get_password(email)`: This function takes an email as an argument and retrieves the hashed account password for the user with the corresponding email address from the ApprovedApplications collection in the MongoDB database.
- `applicant_denied(u_id)`: This function moves the applicant from the SubmittedApplications collection to the DeniedApplications collection in the MongoDB database, then using SendGrid sends a "Denied Applicant" email to the user.
-  `pull_approved_applicants()`: This function retrieves all the documents from the ApprovedApplications collection in the MongoDB database, where the applicant_status.paid field is set to True.
- `send_login_email(uid, input_password)`: This function sends an email to the applicant with their login information after their application has been approved.
-  `send_forgotPassword_email(username, input_password, hashed_password)`: This function sends an email to the applicant with their new password when they request a password reset.

## Tips for Future Developers

- If you face any issues with CORS, review the `origins` list in the CORS middleware configuration and update it accordingly to include the domain of your frontend application.
- When making changes to the database schema or the Applicant model, ensure that the changes are reflected in both the FastAPI endpoint definitions and the MongoDB queries.
- Make sure to handle exceptions and edge cases, such as missing or invalid data, to ensure the stability and reliability of the API.
- Regularly update the dependencies to maintain security and compatibility.



