{
    "banner": {
        "logo_url": "https://cdn.yourcmp.com/logos/client123.png",
        "banner_text": "We use cookies to improve your experience.",
        "links": [{"text": "Privacy Policy", "url": "https://example.com/privacy"}, {"text": "Cookie Policy", "url": "https://example.com/cookies"}],
    },
    "preference": {
        "title": "Manage Your Preferences",
        "description": "You can choose which types of cookies to allow below. You can update your preferences anytime.",
        "links": [{"text": "Learn More", "url": "https://example.com/learn-more"}],
        "categories": [
            {
                "id": "necessary",
                "name": "Strictly Necessary Cookies",
                "description": "These cookies are essential for the website to function and cannot be disabled.",
                "required": True,
                "cookies": [
                    {"name": "session_id", "description": "Maintains session state between page loads.", "domain": "example.com"},
                    {"name": "csrf_token", "description": "Protects against cross-site request forgery attacks.", "domain": "example.com"},
                ],
            },
            {
                "id": "analytics",
                "name": "Analytics Cookies",
                "description": "These cookies help us understand how visitors interact with our website.",
                "required": False,
                "cookies": [
                    {"name": "_ga", "description": "Used by Google Analytics to track user behavior.", "domain": ".google.com"},
                    {"name": "_gid", "description": "Used to distinguish users for analytics purposes.", "domain": ".google.com"},
                ],
            },
            {
                "id": "marketing",
                "name": "Marketing Cookies",
                "description": "These cookies are used to deliver targeted advertisements.",
                "required": False,
                "cookies": [{"name": "fbp", "description": "Facebook Pixel cookie used for remarketing.", "domain": ".facebook.com"}],
            },
        ],
    },
}
