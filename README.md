# BlackWomenMDNetwork

The BWMDN Backend API is a FastAPI based backend application to manage applications, authentication, and file uploads for the DivaDocs platform. The project uses MongoDB to store and manage the data. There are various endpoints to handle the multitude of different functions across the website.


## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Current State](#current-state)
- [Tips for Future Developers](#tips-for-future-developers)

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7 or higher
- MongoDB Atlas Account and Cluster
- Stripe Account
- SendGrid Account

## Overview of Software Modules

1. `main.py`: This is the main entry point of the application. It initializes and runs the web server, defines the API endpoints, and handles the requests and responses.

2. `mongo_test.py`: This module is responsible for connecting to the MongoDB database, handling database operations, and providing an interface for other modules to interact with the data.

3. `models.py`: This module contains the data models and schemas used throughout the application, including Pydantic models and Enums for input validation and serialization.

## Flow Chart
`main.py` depends on `mongo_test.py` for database operations, and `mongo_test.py` depends on `models.py` for data models and schemas.


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
git clone https://github.com/your-username/divadocs-api.git
```

2. Navigate to the cloned directory


3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Run the FastAPI server:
```
python3 main.py
```
or
```
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```


5. Visit http://127.0.0.1:5000/docs to access the Swagger UI for API documentation and testing.

## API Endpoints

The API includes the following endpoints:

- `/applicants/add`: Store applicant information
- `/applicants/view`: View all applicants
- `/applicants/view/{id}`: View a specific applicant by ID
- `/applicants/resume/upload`: Upload applicant resume (PDF)
- `/applicants/downloadresume/{name_file}`: Download applicant resume
- `/applicants/approveapplicant`: Request payment from the applicant
- `/webhook`: Stripe webhook endpoint
- `/login`: Authenticate users and generate JWT tokens
- `/admin_login`: Authenticate admin users and generate JWT tokens
- `/protected_endpoint`: Example of a protected endpoint that requires JWT authentication
- `/applicants/declineapplicant`: Decline an applicant
- `/membershipapplicants/view`: View all approved applicants

## Current State

## Tips for Future Developers

- If you face any issues with CORS, review the `origins` list in the CORS middleware configuration and update it accordingly to include the domain of your frontend application.
- When making changes to the database schema or the Applicant model, ensure that the changes are reflected in both the FastAPI endpoint definitions and the MongoDB queries.
- Make sure to handle exceptions and edge cases, such as missing or invalid data, to ensure the stability and reliability of the API.
- Regularly update the dependencies to maintain security and compatibility.



