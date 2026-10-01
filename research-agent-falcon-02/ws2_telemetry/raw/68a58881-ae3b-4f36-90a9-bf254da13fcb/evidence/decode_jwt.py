import base64, json
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcxNjNiYzEtNDdmZC00MjMzLThjOWUtMzhmOTIwOTJjMzg0IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjQ1NiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjk4MTI3fQ.ng3yoW7W0eiiF221GvnHIx0EX-BA6jixecJzsTVFY3Q'
header, payload, sig = token.split('.')
for part in [header, payload]:
    padded = part + '=' * (-len(part) % 4)
    decoded = base64.urlsafe_b64decode(padded)
    print(json.dumps(json.loads(decoded), indent=2))