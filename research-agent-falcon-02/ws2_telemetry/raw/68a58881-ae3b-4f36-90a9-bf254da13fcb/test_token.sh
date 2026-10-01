#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY5Mzg2NH0.RQ1vk-q1HI1seiyjM3_iHDPh5bXaBty2jHtoM9cXGYQ"
curl -s -i -H "Authorization: Bearer $TOKEN" "https://duck-store.escape.tech/api/v1/admin/users"