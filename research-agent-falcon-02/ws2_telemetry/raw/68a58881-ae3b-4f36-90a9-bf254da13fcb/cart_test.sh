#!/bin/bash
TOKEN_A="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWQ2MzFhZWItYWMxNi00MDhkLThlNmUtZTFkZmU1NjUyZTY1IiwidXNlcm5hbWUiOiJ1c2VyYV8xNzkwNjkxNTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2OTMzOTh9.bi3oGTNIWLEs2cexT_OAtHZy-B_q7lGguWbQDXq-EEU"
curl -s -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" https://duck-store.escape.tech/api/v1/cart/