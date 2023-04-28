import requests

url = 'https://se-diva-docs.herokuapp.com/approvedapplicants/view'

payload = {}

headers = {'Authorization': 'Bearer i_am_a_fake_token' }
response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
