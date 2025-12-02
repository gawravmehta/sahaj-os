import json
import random
from locust import HttpUser, task, between

# Base URL for the backend-notice service.
# This should be replaced with the actual URL of your backend-notice instance
# (e.g., "http://localhost:8000" or your production/staging URL).
BASE_URL = "http://localhost:8000" # Placeholder - **UPDATE THIS TO YOUR ACTUAL BACKEND-NOTICE SERVICE URL**

class BackendNoticeUser(HttpUser):
    host = BASE_URL
    wait_time = between(1, 3)  # Simulate user think time between tasks (1 to 3 seconds)

    # Placeholder for a valid JWT token. In a real load test, this token
    # would be dynamically obtained, e.g., by first calling an authentication endpoint.
    # For demonstration, we use a static placeholder.
    # IMPORTANT: Replace with a token that is actually valid for your system in a test environment.
    VALID_TOKEN_PLACEHOLDER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    # Placeholder for a valid OTP that your system might generate.
    # In a real test, you might need to mock OTP generation or capture it from logs/other services.
    VALID_OTP_PLACEHOLDER = "123456"

    # Define a list of dummy df_ids, dp_ids, and request_ids for dynamic payload generation
    DUMMY_IDS = [
        {"df_id": f"df_{i}", "dp_id": f"dp_{i}", "request_id": f"req_{i}"} for i in range(1, 101)
    ]

    @task(5) # Higher weight, as fetching notice is a common action
    def get_notice(self):
        """
        Simulates fetching the consent notice HTML page.
        Corresponds to GET /api/v1/n/get-notice/{token}
        """
        token = self.VALID_TOKEN_PLACEHOLDER # Use a valid token
        self.client.get(
            f"/api/v1/n/get-notice/{token}",
            name="/api/v1/n/get-notice/[token]",
            catch_response=True # Capture response to check for status codes or content
        )

    @task(3)
    def get_otp_page(self):
        """
        Simulates fetching the OTP verification page HTML.
        Corresponds to GET /api/v1/n/get-otp-page/{token}
        """
        token = self.VALID_TOKEN_PLACEHOLDER # Use a valid token
        self.client.get(
            f"/api/v1/n/get-otp-page/{token}",
            name="/api/v1/n/get-otp-page/[token]",
            catch_response=True
        )

    @task(2)
    def verify_otp(self):
        """
        Simulates submitting an OTP for verification.
        Corresponds to POST /api/v1/n/verify-otp
        """
        token = self.VALID_TOKEN_PLACEHOLDER # Use a valid token
        otp = self.VALID_OTP_PLACEHOLDER # Use a valid OTP
        # The endpoint expects token and otp as query parameters
        self.client.post(
            f"/api/v1/n/verify-otp?token={token}&otp={otp}",
            name="/api/v1/n/verify-otp",
            catch_response=True
        )

    @task(4)
    def submit_consent(self):
        """
        Simulates submitting user consent.
        Corresponds to POST /api/v1/n/submit-consent
        """
        token_model = {"token": self.VALID_TOKEN_PLACEHOLDER} # Dynamically generated valid token
        self.client.post(
            "/api/v1/n/submit-consent",
            json=token_model,
            name="/api/v1/n/submit-consent",
            catch_response=True
        )

    @task(1) # Lower weight, as this is typically an internal webhook acknowledgment
    def dp_verification_ack(self):
        """
        Simulates the DP verification acknowledgment webhook.
        Corresponds to POST /api/v1/n/dp-verification-ack
        This requires a valid signature and timestamp. For a real test,
        these would need to be accurately generated/mocked.
        """
        # Select random IDs for dynamic payload
        ids = random.choice(self.DUMMY_IDS)
        payload = {
            "df_id": ids["df_id"],
            "dp_id": ids["dp_id"],
            "request_id": ids["request_id"],
            "ack_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        # In a real scenario, x_df_signature would be a valid HMAC-SHA256 signature
        # computed based on the payload and a shared secret.
        # For simplicity, we use a dummy signature here.
        headers = {"X-DF-Signature": "dummy_signature_123"}
        self.client.post(
            "/api/v1/n/dp-verification-ack",
            json=payload,
            headers=headers,
            name="/api/v1/n/dp-verification-ack",
            catch_response=True
        )

    @task(1) # Lower weight, as legacy endpoints might be less frequently used
    def get_legacy_notice(self):
        """
        Simulates fetching a legacy consent notice.
        Corresponds to GET /api/v1/n/{sender_id}?token={token}
        """
        sender_id = "your_sender_id" # Replace with actual sender ID
        token = self.VALID_TOKEN_PLACEHOLDER # Use a valid token
        self.client.get(
            f"/api/v1/n/{sender_id}?token={token}",
            name="/api/v1/n/legacy-notice/[sender_id]",
            catch_response=True
        )

    @task(1)
    def submit_legacy_consent(self):
        """
        Simulates submitting legacy consent.
        Corresponds to POST /api/v1/n/submit-legacy-consent
        """
        token_model = {"token": self.VALID_TOKEN_PLACEHOLDER} # Dynamically generated valid token
        self.client.post(
            "/api/v1/n/submit-legacy-consent",
            json=token_model,
            name="/api/v1/n/submit-legacy-consent",
            catch_response=True
        )

    @task(1)
    def manage_legacy_notice(self):
        """
        Simulates fetching the legacy notice management page.
        Corresponds to GET /api/v1/n/mln/{token}
        """
        token = self.VALID_TOKEN_PLACEHOLDER # Use a valid token
        self.client.get(
            f"/api/v1/n/mln/{token}",
            name="/api/v1/n/mln/[token]",
            catch_response=True
        )

    @task(1) # Typically a redirect, so its direct load is less about content and more about redirect performance
    def authenticate_and_redirect(self):
        """
        Simulates the authentication endpoint which redirects to get-notice.
        Corresponds to GET /api/v1/n/authenticate
        """
        # This endpoint expects query parameters like df_id, dp_id, request_id, cp_id, etc.
        # For a full simulation, these would need to be dynamic.
        # For simplicity, we use placeholders.
        query_params = {
            "df_id": "dummy_df_id",
            "dp_id": "dummy_dp_id",
            "request_id": "dummy_request_id",
            "cp_id": "dummy_cp_id",
            "lang": "en",
            "country_code": "US",
            "redirect_url": "http://example.com/success",
            "fail_redirect_url": "http://example.com/fail"
        }
        self.client.get(
            "/api/v1/n/authenticate",
            params=query_params,
            name="/api/v1/n/authenticate",
            allow_redirects=False, # We usually want to test the redirect itself, not follow it
            catch_response=True
        )

# How to run these tests:
# 1. Ensure you have Locust installed (`pip install locust`).
# 2. Save this file as `locustfile.py` in a directory (e.g., `load_tests/backend-notice/`).
# 3. Open your terminal in that directory.
# 4. Run Locust using the command: `locust -f locustfile.py`
# 5. Open your web browser and go to http://localhost:8089 (the default Locust UI).
# 6. Enter the host (e.g., "http://localhost:8000" if your backend-notice is running there)
#    and the desired number of users and spawn rate, then start the swarm.
#
# Remember to replace placeholder tokens, OTPs, and dynamic data generation
# with actual logic that fits your application's requirements for a realistic test.
