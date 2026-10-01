#!/bin/bash
TOKEN_A="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkwNTk2M2UtYzVhZS00YjdmLTg2YjctNzAwZmQ2ZDRkOTlkIiwidXNlcm5hbWUiOiJ2YXB0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY2ODY5M30.Vf_2xplwfqQw7o9VLAMI3dLctn4E7X-tsz1tkLsEFBA"
curl -s -H "Authorization: Bearer $TOKEN_A" "https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=10"