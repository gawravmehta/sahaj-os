export const options = {
    geographicScope: [
      {
        value: "andaman and Nicobar Islands",
        label: "Andaman and Nicobar Islands",
      },
      { value: "andhra Pradesh", label: "Andhra Pradesh" },
      { value: "arunachal Pradesh", label: "Arunachal Pradesh" },
      { value: "assam", label: "Assam" },
      { value: "bihar", label: "Bihar" },
      { value: "chandigarh", label: "Chandigarh" },
      { value: "chhattisgarh", label: "Chhattisgarh" },
      { value: "delhi", label: "Delhi" },
      { value: "goa", label: "Goa" },
      { value: "gujarat", label: "Gujarat" },
      { value: "haryana", label: "Haryana" },
      { value: "himachal Pradesh", label: "Himachal Pradesh" },
      { value: "jharkhand", label: "Jharkhand" },
      { value: "karnataka", label: "Karnataka" },
      { value: "kerala", label: "Kerala" },
      { value: "lakshadweep", label: "Lakshadweep" },
      { value: "maharashtra", label: "Maharashtra" },
      { value: "manipur", label: "Manipur" },
      { value: "meghalaya", label: "Meghalaya" },
      { value: "mizoram", label: "Mizoram" },
      { value: "madhya Pradesh", label: "Madhya Pradesh" },
      { value: "nagaland", label: "Nagaland" },
      { value: "odisha", label: "Odisha" },
      { value: "punjab", label: "Punjab" },
      { value: "rajasthan", label: "Rajasthan" },
      { value: "sikkim", label: "Sikkim" },
      { value: "tamil Nadu", label: "Tamil Nadu" },
      { value: "telangana", label: "Telangana" },
      { value: "tripura", label: "Tripura" },
      { value: "uttar Pradesh", label: "Uttar Pradesh" },
      { value: "uttarakhand", label: "Uttarakhand" },
      { value: "west Bengal", label: "West Bengal" },
      { value: "puducherry", label: "Puducherry" },
    ],
  
    priority: [
      { value: "high", label: "High" },
      { value: "medium", label: "Medium" },
      { value: "low", label: "Low" },
    ],
    frequency: [
      { value: "monthly", label: "Monthly" },
      { value: "half-yearly", label: "Half Yearly" },
      { value: "quarterly", label: "Quarterly" },
    ],
    businessFunction: [
      { value: "Sales", label: "Sales" },
      { value: "Marketing", label: "Marketing" },
      { value: "Product Development", label: "Product Development" },
      { value: "Customer Support", label: "Customer Support" },
      { value: "Operations", label: "Operations" },
      { value: "Finance", label: "Finance" },
      { value: "Human Resources", label: "Human Resources" },
      { value: "IT Support", label: "IT Support" },
      { value: "Legal", label: "Legal" },
      { value: "Procurement", label: "Procurement" },
      { value: "Business Strategy", label: "Business Strategy" },
      { value: "R&D", label: "Research and Development" },
      { value: "Compliance", label: "Compliance" },
      { value: "Quality Assurance", label: "Quality Assurance" },
      { value: "Supply Chain Management", label: "Supply Chain Management" },
      { value: "Logistics", label: "Logistics" },
      { value: "Customer Success", label: "Customer Success" },
      { value: "Business Analytics", label: "Business Analytics" },
      { value: "Data Science", label: "Data Science" },
      { value: "Project Management", label: "Project Management" },
      { value: "Administration", label: "Administration" },
      { value: "Risk Management", label: "Risk Management" },
      { value: "Strategy and Planning", label: "Strategy and Planning" },
      { value: "Corporate Affairs", label: "Corporate Affairs" },
      { value: "Mergers and Acquisitions", label: "Mergers and Acquisitions" },
      { value: "Investor Relations", label: "Investor Relations" },
      { value: "Public Relations", label: "Public Relations" },
      { value: "Sustainability", label: "Sustainability" },
      { value: "Business Development", label: "Business Development" },
    ],
    dependency: [
        { value: "Dependency 1", label: "Dependency 1" },
        { value: "Dependency 2", label: "Dependency 2" },
        { value: "Dependency 3", label: "Dependency 3" },
        { value: "Dependency 4", label: "Dependency 4" },
        { value: "Dependency 5", label: "Dependency 5" },
      ],
    
      retention: [
        { value: "retention 1", label: "Retention 1" },
        { value: "retention 2", label: "Retention 2" },
      ],
    
      consent: [
        { value: "year", label: "Year" },
        { value: "month", label: "Month" },
        { value: "days", label: "Days" },
      ],


      
      purpose_category: [
          { label: "Core Service & Operations", value: "Core Service & Operations" },
          { label: "Compliance, Legal & Risk", value: "Compliance, Legal & Risk" },
          { label: "Marketing, Sales & Engagement", value: "Marketing, Sales & Engagement" },
          { label: "Data Sharing & Ecosystem", value: "Data Sharing & Ecosystem" },
          { label: "Community, Social & Engagement", value: "Community, Social & Engagement" },
          { label: "Sensitive Processing", value: "Sensitive Processing" },
          { label: "Analytics, AI & Innovation", value: "Analytics, AI & Innovation" },
          { label: "People, HR & Governance", value: "People, HR & Governance" },
          { label: "Public Interest & CSR", value: "Public Interest & CSR" },
          { label: "Product, Service & Experience Personalization", value: "Product, Service & Experience Personalization" },
          { label: "Financial, Credit & Commercial Services", value: "Financial, Credit & Commercial Services" },
          { label: "Security, Monitoring & Enforcement", value: "Security, Monitoring & Enforcement" },
          { label: "Cross-Border & Ecosystem Expansion", value: "Cross-Border & Ecosystem Expansion" },
          { label: "Consumer Insights & Market Research", value: "Consumer Insights & Market Research" },
          { label: "Education, Training & Upskilling", value: "Education, Training & Upskilling" },
          { label: "Infrastructure, IoT & Smart Systems", value: "Infrastructure, IoT & Smart Systems" },
          { label: "Media, Entertainment & Lifestyle", value: "Media, Entertainment & Lifestyle" },
          { label: "Data Brokerage & Commercial Monetization", value: "Data Brokerage & Commercial Monetization" },
          { label: "Future Technologies & Emerging Areas", value: "Future Technologies & Emerging Areas" }
        ],
      
        purpose_sub_category: {
          "Core Service & Operations": [
            { label: "Core Service Delivery & Account Management", value: "Core Service Delivery & Account Management" },
            { label: "User Identity Verification & OTPs", value: "User Identity Verification & OTPs" },
            { label: "Know Your Customer (KYC)", value: "Know Your Customer (KYC)" },
            { label: "Know Your Business (KYB)", value: "Know Your Business (KYB)" },
            { label: "Payments, Billing & Settlements", value: "Payments, Billing & Settlements" },
            { label: "Logistics, Fulfilment & Field Operations", value: "Logistics, Fulfilment & Field Operations" },
            { label: "Customer Support & Grievance Redressal", value: "Customer Support & Grievance Redressal" },
            { label: "Transactional & Service Communications", value: "Transactional & Service Communications" },
            { label: "Record Retention, Archiving & Backup", value: "Record Retention, Archiving & Backup" }
          ],
          "Compliance, Legal & Risk": [
            { label: "Compliance, Audit & Regulatory Reporting", value: "Compliance, Audit & Regulatory Reporting" },
            { label: "Security, Fraud & Abuse Prevention", value: "Security, Fraud & Abuse Prevention" },
            { label: "Cross-Border Data Transfers", value: "Cross-Border Data Transfers" },
            { label: "Insurance & Risk Management", value: "Insurance & Risk Management" },
            { label: "Intellectual Property Protection", value: "Intellectual Property Protection" }
          ],
          "Marketing, Sales & Engagement": [
            { label: "Marketing, Promotions & Outreach", value: "Marketing, Promotions & Outreach" },
            { label: "Advertising & Cross-Site Personalization", value: "Advertising & Cross-Site Personalization" },
            { label: "First-Party Personalization", value: "First-Party Personalization" },
            { label: "Analytics & Product Improvement", value: "Analytics & Product Improvement" },
            { label: "Experiments, Research & Testing", value: "Experiments, Research & Testing" },
            { label: "B2B Sales Enablement", value: "B2B Sales Enablement" },
            { label: "Publicity, Testimonials & Case Studies", value: "Publicity, Testimonials & Case Studies" },
            { label: "Loyalty, Affiliates & Cross-Selling", value: "Loyalty, Affiliates & Cross-Selling" },
            { label: "Sponsorships & Co-Branded Initiatives", value: "Sponsorships & Co-Branded Initiatives" }
          ],
          "Data Sharing & Ecosystem": [
            { label: "Third-Party Processing, Vendors & Affiliates", value: "Third-Party Processing, Vendors & Affiliates" },
            { label: "Interoperability, Portability & Data Exchange", value: "Interoperability, Portability & Data Exchange" },
            { label: "Open Data, Transparency & Public Disclosure", value: "Open Data, Transparency & Public Disclosure" }
          ],
          "Community, Social & Engagement": [
            { label: "Social Features & Community", value: "Social Features & Community" },
            { label: "Content Creation, Curation & Publishing", value: "Content Creation, Curation & Publishing" },
            { label: "Gamification, Rewards & Incentives", value: "Gamification, Rewards & Incentives" },
            { label: "Community Governance & Voting", value: "Community Governance & Voting" },
            { label: "Events, Webinars & Offline Engagements", value: "Events, Webinars & Offline Engagements" }
          ],
          "Sensitive Processing": [
            { label: "Automated Decision-Making & Profiling", value: "Automated Decision-Making & Profiling" },
            { label: "Financial Profiling & Credit Scoring", value: "Financial Profiling & Credit Scoring" },
            { label: "Health, Wellness & Medical Services", value: "Health, Wellness & Medical Services" },
            { label: "Children’s Data & Parental Consent", value: "Children’s Data & Parental Consent" },
            { label: "Biometric Access & Authentication", value: "Biometric Access & Authentication" },
            { label: "Digital Identity & Wallet Integration", value: "Digital Identity & Wallet Integration" },
            { label: "Location-Based Services & Geofencing", value: "Location-Based Services & Geofencing" },
            { label: "Device & Sensor Access", value: "Device & Sensor Access" }
          ],
          "Analytics, AI & Innovation": [
            { label: "Training of AI/ML Models", value: "Training of AI/ML Models" },
            { label: "Behavioral & Sentiment Analysis", value: "Behavioral & Sentiment Analysis" },
            { label: "Digital Twin & Simulation", value: "Digital Twin & Simulation" },
            { label: "Anonymization, Statistics & Reporting", value: "Anonymization, Statistics & Reporting" }
          ],
          "People, HR & Governance": [
            { label: "Employment & Contractor Management", value: "Employment & Contractor Management" },
            { label: "Vendor Management, Procurement & B2B Operations", value: "Vendor Management, Procurement & B2B Operations" },
            { label: "Knowledge Management & Internal Training", value: "Knowledge Management & Internal Training" },
            { label: "Ethics & Diversity Monitoring", value: "Ethics & Diversity Monitoring" }
          ],
          "Public Interest & CSR": [
            { label: "Sustainability, ESG & CSR Tracking", value: "Sustainability, ESG & CSR Tracking" },
            { label: "Philanthropy & Donations", value: "Philanthropy & Donations" },
            { label: "Emergency & Disaster Response", value: "Emergency & Disaster Response" },
            { label: "Lifestyle & Wellness Programs", value: "Lifestyle & Wellness Programs" },
            { label: "Content Moderation, Trust & Safety", value: "Content Moderation, Trust & Safety" }
          ],
          "Product, Service & Experience Personalization": [
            { label: "Adaptive User Interfaces & Accessibility", value: "Adaptive User Interfaces & Accessibility" },
            { label: "Recommendation Engines (Content, Products, Services)", value: "Recommendation Engines (Content, Products, Services)" },
            { label: "Contextual & Situational Personalization (e.g., time, weather, device state)", value: "Contextual & Situational Personalization (e.g., time, weather, device state)" },
            { label: "Multi-Device Continuity & Cross-Channel Sync", value: "Multi-Device Continuity & Cross-Channel Sync" },
            { label: "Voice, Chatbot & Conversational Interfaces", value: "Voice, Chatbot & Conversational Interfaces" }
          ],
          "Financial, Credit & Commercial Services": [
            { label: "Payments Facilitation & Credit Extensions", value: "Payments Facilitation & Credit Extensions" },
            { label: "BNPL (Buy Now, Pay Later) & Micro-Finance Services", value: "BNPL (Buy Now, Pay Later) & Micro-Finance Services" },
            { label: "Taxation, Invoicing & Financial Reporting", value: "Taxation, Invoicing & Financial Reporting" },
            { label: "Lending, Debt Collection & Recovery Services", value: "Lending, Debt Collection & Recovery Services" },
            { label: "Investment, Savings & Financial Planning Tools", value: "Investment, Savings & Financial Planning Tools" }
          ],
          "Security, Monitoring & Enforcement": [
            { label: "CCTV, Surveillance & Workplace Monitoring", value: "CCTV, Surveillance & Workplace Monitoring" },
            { label: "Access Controls & Digital Rights Management (DRM)", value: "Access Controls & Digital Rights Management (DRM)" },
            { label: "Employee Monitoring & Productivity Tools", value: "Employee Monitoring & Productivity Tools" },
            { label: "Incident Response & Breach Notifications", value: "Incident Response & Breach Notifications" },
            { label: "Forensic Investigations & Evidence Collection", value: "Forensic Investigations & Evidence Collection" }
          ],
          "Cross-Border & Ecosystem Expansion": [
            { label: "International Roaming & Telecom Services", value: "International Roaming & Telecom Services" },
            { label: "Multi-Jurisdictional Compliance & Disclosures", value: "Multi-Jurisdictional Compliance & Disclosures" },
            { label: "Global Cloud Hosting & Processing Partners", value: "Global Cloud Hosting & Processing Partners" },
            { label: "Government Requests, Law Enforcement & Cooperation", value: "Government Requests, Law Enforcement & Cooperation" },
            { label: "Cross-Border Talent & Contractor Data Sharing", value: "Cross-Border Talent & Contractor Data Sharing" }
          ],
          "Consumer Insights & Market Research": [
            { label: "Panel Participation & Feedback Collection", value: "Panel Participation & Feedback Collection" },
            { label: "Consumer Surveys & Opinion Polls", value: "Consumer Surveys & Opinion Polls" },
            { label: "Social Listening & Trend Analysis", value: "Social Listening & Trend Analysis" },
            { label: "Focus Groups & Usability Studies", value: "Focus Groups & Usability Studies" },
            { label: "Competitive Benchmarking & Industry Reports", value: "Competitive Benchmarking & Industry Reports" }
          ],
          "Education, Training & Upskilling": [
            { label: "Online Learning & Skill Platforms", value: "Online Learning & Skill Platforms" },
            { label: "Credentialing & Certification Tracking", value: "Credentialing & Certification Tracking" },
            { label: "Student Performance Analytics & Reports", value: "Student Performance Analytics & Reports" },
            { label: "Internship, Placement & Career Matching", value: "Internship, Placement & Career Matching" },
            { label: "Alumni Networks & Mentorship Programs", value: "Alumni Networks & Mentorship Programs" }
          ],
          "Infrastructure, IoT & Smart Systems": [
            { label: "Connected Devices & IoT Integrations", value: "Connected Devices & IoT Integrations" },
            { label: "Smart Homes, Offices & Cities Data Processing", value: "Smart Homes, Offices & Cities Data Processing" },
            { label: "Wearables & Health Trackers", value: "Wearables & Health Trackers" },
            { label: "Telematics, Fleet & Vehicle Tracking", value: "Telematics, Fleet & Vehicle Tracking" },
            { label: "AR/VR & Immersive Experience Tracking", value: "AR/VR & Immersive Experience Tracking" }
          ],
          "Media, Entertainment & Lifestyle": [
            { label: "Streaming Services & Content Recommendations", value: "Streaming Services & Content Recommendations" },
            { label: "Gaming & Esports Engagement Tracking", value: "Gaming & Esports Engagement Tracking" },
            { label: "Ticketing, Reservations & Bookings", value: "Ticketing, Reservations & Bookings" },
            { label: "Celebrity Endorsements & Influencer Collaborations", value: "Celebrity Endorsements & Influencer Collaborations" },
            { label: "Fashion, Travel & Lifestyle Personalization", value: "Fashion, Travel & Lifestyle Personalization" }
          ],
          "Data Brokerage & Commercial Monetization": [
            { label: "Data Licensing & Partnerships", value: "Data Licensing & Partnerships" },
            { label: "Marketplaces & Third-Party Resale", value: "Marketplaces & Third-Party Resale" },
            { label: "Pseudonymized & Aggregated Insights Sharing", value: "Pseudonymized & Aggregated Insights Sharing" },
            { label: "Ad Networks & Demand-Side Platforms (DSPs)", value: "Ad Networks & Demand-Side Platforms (DSPs)" },
            { label: "Revenue-Sharing Agreements Based on Data", value: "Revenue-Sharing Agreements Based on Data" }
          ],
          "Future Technologies & Emerging Areas": [
            { label: "Blockchain, NFTs & Tokenized Identity", value: "Blockchain, NFTs & Tokenized Identity" },
            { label: "Quantum-Safe Data Processing & Encryption", value: "Quantum-Safe Data Processing & Encryption" },
            { label: "Robotics & Automation Data Collection", value: "Robotics & Automation Data Collection" },
            { label: "Space-Tech, Drones & Aerospace Monitoring", value: "Space-Tech, Drones & Aerospace Monitoring" },
            { label: "NeuroTech, Brainwave & Cognitive Tracking", value: "NeuroTech, Brainwave & Cognitive Tracking" }
          ]
        }
  };