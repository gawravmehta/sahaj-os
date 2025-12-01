import json
import random
from locust import HttpUser, task, between
from datetime import datetime, UTC

# Base URL for the cookie-consent-collection service.
# This should be replaced with the actual URL of your instance.
BASE_URL = "http://localhost:8001" # Placeholder - **UPDATE THIS TO YOUR ACTUAL COOKIE-CONSENT-COLLECTION SERVICE URL**

class CookieConsentCollectionUser(HttpUser):
    host = BASE_URL
    wait_time = between(1, 3)  # Simulate user think time between tasks (1 to 3 seconds)

    # Define a list of dummy website_ids for dynamic payload generation
    DUMMY_WEBSITE_IDS = [f"website_{i}" for i in range(1, 51)]

    # Define a list of dummy user_ids for dynamic payload generation (some might be None to simulate IP-based consent)
    DUMMY_USER_IDS = [None] + [f"user_{i}" for i in range(1, 1001)] # Include None for IP-based unique_key

    @task(5) # Higher weight, as consent submission is the primary function
    def submit_consent(self):
        """
        Simulates submitting user cookie consent decisions.
        Corresponds to POST /v1/consent
        """
        user_id_choice = random.choice(self.DUMMY_USER_IDS)
        website_id_choice = random.choice(self.DUMMY_WEBSITE_IDS)

        payload = {
            "category_choices": {
                "necessary": True,
                "analytics": random.choice([True, False]),
                "marketing": random.choice([True, False]),
                "preferences": random.choice([True, False]),
            },
            "website_id": website_id_choice,
            "language": random.choice(["eng", "fra", "deu"]),
        }
        if user_id_choice:
            payload["user_id"] = user_id_choice

        # Headers to simulate x-forwarded-for and user-agent for more realistic auditing
        headers = {
            "Content-Type": "application/json",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/108.0"
            ])
        }

        self.client.post(
            "/v1/consent",
            json=payload,
            headers=headers,
            name="/v1/consent",
            catch_response=True # Capture response to check for status codes or content
        )

    @task(1) # Lower weight, as status checks are less frequent than consent submissions
    def status_check(self):
        """
        Simulates a status check of the service.
        Corresponds to GET /v1/status
        """
        self.client.get(
            "/v1/status",
            name="/v1/status",
            catch_response=True
        )

# How to run these tests:
# 1. Ensure you have Locust installed (`pip install locust`).
# 2. Save this file as `locustfile.py` in a directory (e.g., `load_tests/cookie-consent-collection/`).
# 3. Open your terminal in that directory.
# 4. Run Locust using the command: `locust -f locustfile.py`
# 5. Open your web browser and go to http://localhost:8089 (the default Locust UI).
# 6. Enter the host (e.g., "http://localhost:8001" if your cookie-consent-collection service is running there)
#    and the desired number of users and spawn rate, then start the swarm.
#
# Remember to replace the placeholder `BASE_URL` with your actual service URL.
