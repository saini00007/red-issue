import requests

headers = {"Content-Type": "application/json"}

# Simple GraphQL introspection query
query = "{ __schema { types { name } } }"

resp = requests.post("https://duck-store.escape.tech/graphql", headers=headers, json={"query": query})
print(resp.status_code)
print(resp.text[:5000])