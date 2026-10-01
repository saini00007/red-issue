import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWQ2MzFhZWItYWMxNi00MDhkLThlNmUtZTFkZmU1NjUyZTY1IiwidXNlcm5hbWUiOiJ1c2VyYV8xNzkwNjkxNTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2OTMzOTh9.bi3oGTNIWLEs2cexT_OAtHZy-B_q7lGguWbQDXq-EEU"
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("https://duck-store.escape.tech/api/v1/products", headers=headers)
print(resp.status_code)
print(resp.text[:2000])