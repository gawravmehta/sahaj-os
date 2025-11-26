{
    "en": {
        "banner": {
            "logo_url": "https://cdn.yourcmp.com/logos/client123.png",
            "banner_text": "We use cookies to improve your experience.",
            "links": [
                {"text": "Privacy Policy", "url": "https://example.com/privacy"},
                {"text": "Cookie Policy", "url": "https://example.com/cookies"},
            ],
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
    },
    "hi": {
        "banner": {
            "logo_url": "https://cdn.yourcmp.com/logos/client123.png",
            "banner_text": "हम आपके अनुभव को बेहतर बनाने के लिए कुकीज़ का उपयोग करते हैं।",
            "links": [{"text": "गोपनीयता नीति", "url": "https://example.com/privacy"}, {"text": "कुकी नीति", "url": "https://example.com/cookies"}],
        },
        "preference": {
            "title": "अपनी प्राथमिकताएँ प्रबंधित करें",
            "description": "आप नीचे चुन सकते हैं कि किस प्रकार की कुकीज़ की अनुमति देना चाहते हैं। आप कभी भी अपनी प्राथमिकताएँ अपडेट कर सकते हैं।",
            "links": [{"text": "अधिक जानें", "url": "https://example.com/learn-more"}],
            "categories": [
                {
                    "id": "necessary",
                    "name": "सख्ती से आवश्यक कुकीज़",
                    "description": "ये कुकीज़ वेबसाइट को काम करने के लिए आवश्यक हैं और इन्हें अक्षम नहीं किया जा सकता।",
                    "required": True,
                    "cookies": [
                        {"name": "session_id", "description": "पृष्ठ लोड के बीच सत्र की स्थिति बनाए रखता है।", "domain": "example.com"},
                        {"name": "csrf_token", "description": "क्रॉस-साइट अनुरोध जालसाजी हमलों से सुरक्षा प्रदान करता है।", "domain": "example.com"},
                    ],
                },
                {
                    "id": "analytics",
                    "name": "एनालिटिक्स कुकीज़",
                    "description": "ये कुकीज़ हमें यह समझने में मदद करती हैं कि आगंतुक हमारी वेबसाइट के साथ कैसे इंटरैक्ट करते हैं।",
                    "required": False,
                    "cookies": [
                        {
                            "name": "_ga",
                            "description": "Google Analytics द्वारा उपयोगकर्ता व्यवहार को ट्रैक करने के लिए उपयोग किया जाता है।",
                            "domain": ".google.com",
                        },
                        {
                            "name": "_gid",
                            "description": "एनालिटिक्स उद्देश्यों के लिए उपयोगकर्ताओं को अलग करने के लिए उपयोग किया जाता है।",
                            "domain": ".google.com",
                        },
                    ],
                },
                {
                    "id": "marketing",
                    "name": "मार्केटिंग कुकीज़",
                    "description": "ये कुकीज़ लक्षित विज्ञापनों को प्रदान करने के लिए उपयोग की जाती हैं।",
                    "required": False,
                    "cookies": [{"name": "fbp", "description": "Facebook पिक्सेल कुकी रीमार्केटिंग के लिए उपयोग की जाती है।", "domain": ".facebook.com"}],
                },
            ],
        },
    },
}
