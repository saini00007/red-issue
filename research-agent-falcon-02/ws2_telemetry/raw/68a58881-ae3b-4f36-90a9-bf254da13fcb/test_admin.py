import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzc3NjY3ZjktMjY3OC00MzU1LWJjN2MtODIwYmU4M2U0YzU4IiwidXNlcm5hbWUiOiJhdHRrdXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY4NDcwM30.Eu6rZyvdccrNfPiLt-O6iDbFdX2FWkST4Rteg1yQ4PM"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Try DELETE on testuserB
url = "https://duck-store.escape.tech/api/v1/admin/users/testuserB"
resp = requests.delete(url, headers=headers)
print(f"DELETE {url}: {resp.status_code}")
print(resp.text)

# Try GET on the same
resp = requests.get(url, headers=headers)
print(f"GET {url}: {resp.status_code}")
print(resp.text)