import pymongo

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

    for x in mycol.find():
        print(x)