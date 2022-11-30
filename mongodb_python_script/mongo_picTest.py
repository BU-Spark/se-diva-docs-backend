import pymongo
import gridfs

# Establish Connection to MongoDB

client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

# Select Database

mydb = client["ApplicationForm"]

# Select Collection

mycol = mydb["SubmittedApplications"]

# WRITE picture to the collection in the database

file_location = '/Users/vinaymetlapalli/Desktop/test_file.png'
file_data = open(file_location, "rb")
data =  file_data.read()
fs = gridfs.GridFS(mydb)
fs.put(data, filename = 'test_file.png')
print('upload complete')

# READ picture from the collection in the database & print

data = mydb.fs.files.find_one({'filename' : 'test_file.png'})
my_id = data['_id']
outputdata = fs.get(my_id).read()
download_location = "/Users/vinaymetlapalli/Desktop/" + "MONGO_DL.png"
output = open(download_location, "wb")
output.write(outputdata)
output.close()
print("download complete")
