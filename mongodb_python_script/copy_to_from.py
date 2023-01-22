#import necessary libraries
import pymongo

client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

# Select the database

db1 = client["ApplicationForm"]
db2 = client["MembershipDirectory"]

#select the collections
collection1 = db1["ApprovedApplications"]
collection2 = db2["ActiveUsers"]

#fetch the document that needs to be copied
document = collection1.find_one({"name": target_name})

#copy the document
collection2.insert_one(document)

#verify that the document has been copied
if (collection2.count_documents({}) == 1):
    print("Document has been successfully copied!")
else:
    print("Document copying failed!")
