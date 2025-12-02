from locust import HttpUser, task, between
from urllib.parse import urlparse


class FullFlowUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def full_flow(self):
        # Authentication headers
        client_ip = "192.168.1.100"
        auth_headers = {
            "x-df-key": "Gd0KlIaNXVCdU2Sy",
            "x-df-id": "9f091721-24fc-4f70-9770-c2e9f5623573",
            "x-df-secret": "zkp?x!8T6riEY3tgFgbSp?hnxh20uNUnp25pr$&?2Qo33l!CDL14FeuNVLpzfPvE",
            "X-Forwarded-For": client_ip,  # Add this header to simulate client IP
        }

        # Authentication parameters
        auth_params = {
            "cp_id": "692c333883050d035b147893",
            "dp_id": "a3e1bc2f-8d3e-4a9b-9c41-f6a2e8f3d123",
            "dp_e": "abhishekkhare583@gmail.com",
        }

        # Execute authentication request
        with self.client.get(
            "/api/v1/authenticate",
            params=auth_params,
            headers=auth_headers,
            allow_redirects=False,
            catch_response=True,
        ) as auth_response:

            # Validate authentication response
            if auth_response.status_code != 303:
                auth_response.failure(f"Expected 303, got {auth_response.status_code}")
                return

            redirect_url = auth_response.headers.get("location")
            if not redirect_url:
                auth_response.failure("Missing redirect URL")
                return

        # Extract path from redirect URL
        parsed_url = urlparse(redirect_url)
        notice_path = parsed_url.path
        if parsed_url.query:
            notice_path += "?" + parsed_url.query

        # Execute notice retrieval request (no headers needed for this endpoint)
        with self.client.get(notice_path, headers={"X-Forwarded-For": client_ip}, catch_response=True) as notice_response:

            # Validate notice response
            if notice_response.status_code != 200:
                notice_response.failure(f"Bad status: {notice_response.status_code}")

            # Validate content
            elif "Notice" not in notice_response.text and "Consent" not in notice_response.text:
                notice_response.failure("Missing required content in response")
