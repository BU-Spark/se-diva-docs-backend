import pymongo
import gridfs

# Establish Connection to MongoDB

client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")

# Select Database

mydb = client["MemberPortal"]

# Select Collection

mycol = mydb["application_forms"]

# WRITE picture to the collection in the database

file_location = '/Users/vinaymetlapalli/Desktop/abhinoor.jpg'
file_data = open(file_location, "rb")
data =  file_data.read()
fs = gridfs.GridFS(mydb)
fs.put(data, filename = 'abhinoor.jpg')
print('upload complete')

# READ picture from the collection in the database & print

data = mydb.fs.files.find_one({'filename' : 'abhinoor.jpg'})
my_id = data['_id']
outputdata = fs.get(my_id).read()
download_location = "/Users/vinaymetlapalli/Documents/" + "mongo_test.jpg"
output = open(download_location, "wb")
output.write(outputdata)
output.close()
print("download complete")
