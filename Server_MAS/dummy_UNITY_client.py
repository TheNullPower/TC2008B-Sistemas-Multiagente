# from django.test import Client
#
# c = Client()
# response = c.post('/login/', {'username': 'john', 'password': 'smith'})
# response.status_code
#
# response = c.get('/customer/details/')
# response.content
import pprint
from http.client import HTTPConnection
import json
conn = HTTPConnection("http://localhost", 8585)
print(conn)

conn.request("GET", "/")
response = conn.getresponse()
headers = response.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))

print("Status: {} and reason: {}".format(response.status, response.reason))

fake_agent = {
    "kind": "Ball",
    "colour": "Red",
    "position": {
        "x": 1.0,
        "y": 0.0,
        "z": 2.0
    }
}

headers = {'Content-Type': 'application/json'}

conn.request('POST', '/post', json.dumps(fake_agent), headers)

response = conn.getresponse()
pprint.pprint(response.read().decode())

# conn.close()