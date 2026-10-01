#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjFhYmM5YjEtNzNiYy00OTI3LWIxOTktMzdlYzJjZjI4Zjg2IiwidXNlcm5hbWUiOiJhdHRhY2tlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY1ODkwMX0.EV-ojy8Mvz0_C2k3UT_UU5s--NJUNZvW1H-HvE_0xVI"
curl -s "https://duck-store.escape.tech/api/v1/users/me/profile" -H "Authorization: Bearer $TOKEN" -v