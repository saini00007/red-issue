#!/bin/bash
TOKEN_A=$(cat /work/token_a.txt)
curl -s -X POST "https://duck-store.escape.tech/api/v1/testimonials/" \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test testimonial from verify_user_a", "rating": 5}'