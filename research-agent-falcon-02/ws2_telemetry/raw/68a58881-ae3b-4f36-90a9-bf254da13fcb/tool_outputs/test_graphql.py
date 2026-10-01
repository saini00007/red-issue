import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWQ2MzFhZWItYWMxNi00MDhkLThlNmUtZTFkZmU1NjUyZTY1IiwidXNlcm5hbWUiOiJ1c2VyYV8xNzkwNjkxNTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2OTMzOTh9.bi3oGTNIWLEs2cexT_OAtHZy-B_q7lGguWbQDXq-EEU"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# GraphQL introspection query
query = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      ...FullType
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

resp = requests.post("https://duck-store.escape.tech/graphql", headers=headers, json={"query": query})
print(resp.status_code)
print(resp.text[:5000])