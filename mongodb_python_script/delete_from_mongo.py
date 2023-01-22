# Import the necessary packages
from pymongo import MongoClient

# Establish a connection to the MongoDB server
client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

# Select the database
db = client["ApplicationForm"]

# Select the collection
collection = mydb["SubmittedApplications"]

# Delete the document matching the given filter
collection.delete_one({"name": "John Doe"})
