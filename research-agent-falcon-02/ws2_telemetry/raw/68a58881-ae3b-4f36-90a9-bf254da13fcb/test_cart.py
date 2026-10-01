import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWQ2MzFhZWItYWMxNi00MDhkLThlNmUtZTFkZmU1NjUyZTY1IiwidXNlcm5hbWUiOiJ1c2VyYV8xNzkwNjkxNTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2OTMzOTh9.bi3oGTNIWLEs2cexT_OAtHZy-B_q7lGguWbQDXq-EEU"
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test GET cart
r = requests.get('https://duck-store.escape.tech/api/v1/cart/', headers=headers)
print(f"GET cart: {r.status_code}")
print(r.text)

# Test POST cart/add with normal payload
r = requests.post('https://duck-store.escape.tech/api/v1/cart/add', headers=headers, json={"product_id": 1, "quantity": 1})
print(f"POST cart/add: {r.status_code}")
print(r.text)