#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWQ2MzFhZWItYWMxNi00MDhkLThlNmUtZTFkZmU1NjUyZTY1IiwidXNlcm5hbWUiOiJ1c2VyYV8xNzkwNjkxNTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2OTMzOTh9.bi3oGTNIWLEs2cexT_OAtHZy-B_q7lGguWbQDXq-EEU"
curl -s -X GET "https://duck-store.escape.tech/api/v1/admin/users" -H "Authorization: Bearer $TOKEN" | head -200