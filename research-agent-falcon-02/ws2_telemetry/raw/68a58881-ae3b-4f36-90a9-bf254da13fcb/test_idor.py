import requests
import json

# User A token
user_a_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkwNTk2M2UtYzVhZS00YjdmLTg2YjctNzAwZmQ2ZDRkOTlkIiwidXNlcm5hbWUiOiJ2YXB0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY2ODY5M30.Vf_2xplwfqQw7o9VLAMI3dLctn4E7X-tsz1tkLsEFBA"
user_b_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDkzZDZhMTMtYWNhNi00N2Y5LWE1NTYtZjJhODEwNzY5Mzg2IiwidXNlcm5hbWUiOiJ2YXB0dXNlcjIiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY2ODcxOX0.4cbeVpJHPyyy3J5w9RUmZJSYSPoXTkMN21GqiD_IUek"

base_url = "https://duck-store.escape.tech/api/v1"

headers_a = {"Authorization": f"Bearer {user_a_token}"}
headers_b = {"Authorization": f"Bearer {user_b_token}"}

print("=== User A getting testimonials ===")
r = requests.get(f"{base_url}/testimonials", headers=headers_a)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:2000]}")

print("\n=== User B getting testimonials ===")
r = requests.get(f"{base_url}/testimonials", headers=headers_b)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:2000]}")