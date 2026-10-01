import requests

headers = {"Content-Type": "application/json"}

# Simple GraphQL introspection query
query = "{ __schema { types { name } } }"

resp = requests.post("https://duck-store.escape.tech/graphql", headers=headers, json={"query": query}, allow_redirects=True)
print("Status:", resp.status_code)
print("URL:", resp.url)
print("Headers:", dict(resp.headers))
print("Body:", resp.text[:5000])