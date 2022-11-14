import pymongo

# Establish Connection to MongoDB

client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

# Select Database

mydb = client["MemberPortal"]

# Select Collection

mycol = mydb["application_forms"]

# WRITE to the collection in the database

mydict = { "__id": "test", "First Name": "Test", "Last Name": "Test" }
x = mycol.insert_one(mydict)

# READ from the collection in the database & print

for x in mycol.find():
    print(x)
