import pymongo

client = pymongo.MongoClient("mongodb+srv://vinaydivadocs:divadocs@divadocsmemberportal.zhjdqu2.mongodb.net/?retryWrites=true&w=majority")
client.admin.command('enableSharding', 'ApplicationForm')
#client.admin.command('enableSharding', 'SubmittedApplications')
