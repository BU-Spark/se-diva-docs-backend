import requests

url = 'https://se-diva-docs.herokuapp.com/approvedapplicants/view'
url2 = 'http://127.0.0.1:5000/approvedapplicants/view'

payload = {}

headers = {'Authorization': 'Bearer i_am_a_fake_token' }
response = requests.request("GET", url2, headers=headers, data=payload)

print(response.status_code)
print(response.headers)
print(response.text)
