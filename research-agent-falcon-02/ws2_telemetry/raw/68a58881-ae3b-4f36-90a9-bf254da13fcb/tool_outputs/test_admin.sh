#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTA3NDdkZDUtYTE2YS00N2E2LTlmN2UtZDI5MjA5NzkzMmU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcl9uZXdfMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjk5ODYxfQ.XM028nVCwW_DnbSzn3Dg-1pkSIKKDKuNHoiU6qlFwnU"
curl -s "https://duck-store.escape.tech/api/v1/admin/orders" -H "Authorization: Bearer $TOKEN" | head -200