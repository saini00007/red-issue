import requests

headers = {"Content-Type": "application/json"}

# Simple GraphQL introspection query
query = "{ __schema { types { name } } }"

resp = requests.get("https://duck-store.escape.tech/graphql", params={"query": query}, headers=headers)
print("Status:", resp.status_code)
print("URL:", resp.url)
print("Body:", resp.text[:5000])