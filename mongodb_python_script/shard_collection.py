import pymongo

client = pymongo.MongoClient()
client.admin.command('enableSharding', 'ApplicationForm')
client.admin.command('enableSharding', 'SubmittedApplications')
