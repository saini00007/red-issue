#!/bin/bash
TOKEN_A="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjJiOTRkMmQtZTYxYi00MjA2LTkyZDgtYmY4NmEzMjY3N2U3IiwidXNlcm5hbWUiOiJ2ZXJpZnlfdXNlcl9hIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NjM1NDR9.ow4pRwWqv8HbRuGW2pvoH2d6H8LZEX0k5_Sj8PaR1Z8"
curl -v -X POST "https://duck-store.escape.tech/api/v1/testimonials/" \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test testimonial from verify_user_a", "rating": 5}'