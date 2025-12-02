import json
import random
from locust import HttpUser, task, between


BASE_URL = "http://127.0.0.1:8001"


class CookieConsentCollectionUser(HttpUser):
    host = BASE_URL
    wait_time = between(0.2, 1.2)

    # Dummy data pools
    DUMMY_WEBSITE_IDS = [f"website_{i}" for i in range(1, 51)]
    DUMMY_USER_IDS = [None] + [f"user_{i}" for i in range(1, 1001)]

    @task(5)
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

        headers = {
            "Content-Type": "application/json",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "User-Agent": random.choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/108.0",
                ]
            ),
        }

        with self.client.post("/v1/consent", json=payload, headers=headers, name="/v1/consent", catch_response=True) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Consent failed: {response.status_code} - {response.text}")
            else:
                response.success()

    @task(1)
    def status_check(self):
        """
        Simulates GET /v1/status
        """
        with self.client.get("/v1/status", name="/v1/status", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Status check failed: {response.status_code}")
            else:
                response.success()
