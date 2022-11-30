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

    data =  file

    fs = gridfs.GridFS(mydb)

    fs.put(data, filename = file_name)

def download_file_from_mongo(database):

    # Establish Connection to MongoDB

    client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

    mydb = client[database]

    output_list = []

    for x in mydb.fs.files.find({}):
        my_id = x['_id']
        outputdata = fs.get(my_id).read()
        output_list.append(outputdata)

    return output_list
