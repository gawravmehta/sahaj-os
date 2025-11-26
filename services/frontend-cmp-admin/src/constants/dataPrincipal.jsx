export const basisOptions = [
  { value: "explicit_consent", label: "Explicit Consent" },
  { value: "implicit_consent", label: "Implicit Consent" },
  { value: "contract_performance", label: "Performance of Contract" },
  { value: "legal_obligation", label: "Legal Obligation" },
  { value: "legitimate_interest", label: "Legitimate Interest" },
  { value: "vital_interests", label: "Vital Interests" },
  {
    value: "public_interest",
    label: "Public Interest/Official Duty",
  },
  {
    value: "employment_related",
    label: "Employment-Related Purpose",
  },
  {
    value: "voluntary_disclosure",
    label: "Voluntary Disclosure",
  },
  {
    value: "emergencies",
    label: "Emergencies (e.g., disaster, medical, or public health)",
  },
  {
    value: "judicial_purpose",
    label: "Judicial or Quasi-Judicial Purpose",
  },
  {
    value: "archiving_research",
    label: "Archiving, Research, or Statistical Purposes",
  },
];
export const encryptionOptions = [
  { value: "AES-128", label: "AES-128" },
  { value: "AES-192", label: "AES-192" },
  { value: "AES-256", label: "AES-256" },
  { value: "3DES", label: "3DES" },
  { value: "Blowfish", label: "Blowfish" },
  { value: "Twofish", label: "Twofish" },
  { value: "RSA-2048", label: "RSA-2048" },
  { value: "RSA-4096", label: "RSA-4096" },
  { value: "ECC", label: "ECC (Elliptic Curve Cryptography)" },
  {
    value: "ECDSA",
    label: "ECDSA (Elliptic Curve Digital Signature Algorithm)",
  },
  { value: "ECDH", label: "ECDH (Elliptic Curve Diffie-Hellman)" },
  {
    value: "EdDSA",
    label: "EdDSA (Edwards-curve Digital Signature Algorithm)",
  },
  { value: "DSA", label: "DSA (Digital Signature Algorithm)" },
  { value: "Diffie-Hellman", label: "Diffie-Hellman" },
  { value: "ElGamal", label: "ElGamal" },
  { value: "DES", label: "DES (Data Encryption Standard) - Insecure" },
  { value: "RC4", label: "RC4 (Rivest Cipher 4) - Insecure" },
  { value: "TLS", label: "TLS (Transport Layer Security)" },
  { value: "IPsec", label: "IPsec (Internet Protocol Security)" },
  { value: "WPA2", label: "WPA2 (Wi-Fi Protected Access 2)" },
  { value: "WPA3", label: "WPA3 (Wi-Fi Protected Access 3)" },
  {
    value: "S-MIME",
    label: "S/MIME (Secure/Multipurpose Internet Mail Extensions)",
  },
  { value: "PGP", label: "PGP (Pretty Good Privacy)" },
  { value: "GPG", label: "GPG (GNU Privacy Guard)" },
];

export const consentOptions = [
  { value: "year", label: "Year" },
  { value: "month", label: "Month" },
  { value: "days", label: "Days" },
];

export const rawDomainOptions = [
  "\tuser profile",
  "Account Information",
  "Advertising",
  "Analytics",
  "Authentication",
  "Banking",
  "Billing",
  "Biometrics",
  "Business Registration",
  "Communication",
  "Communications",
  "Contact Information",
  "Credit Rating",
  "Customer Data",
  "Customer Relations",
  "Cybersecurity",
  "Developer Tools",
  "Device Tracking",
  "Digital Wallet",
  "E-commerce",
  "Elections",
  "Employment",
  "Finance",
  "Financial",
  "Financial Information",
  "Financial Regulation",
  "Financial Services",
  "Government ID",
  "HR",
  "Health",
  "Healthcare",
  "Identification",
  "Identity",
  "Identity Verification",
  "Insurance",
  "Location Services",
  "Loyalty Programs",
  "Medical Records",
  "Networking",
  "Non-Profit Organizations",
  "Online Activity",
  "Online Service Account",
  "Payments",
  "Personal Identification",
  "Security",
  "Social Media",
  "Taxation",
  "Telecommunications",
  "Tracking",
  "Transportation",
  "User Authentication",
  "Utilities",
  "Vehicle Information",
  "Vehicle Registration",
  "aarfdiughiuhui",
  "account information",
  "asccsa",
  "ascsac",
  "authentication",
  "banking",
  "behavioral / analytics",
  "biometrics",
  "credit rating",
  "customer data",
  "customer information",
  "customer relations",
  "demographic",
  "device & technical",
  "device security",
  "dssdfh",
  "e-commerce & transactions",
  "education",
  "employment",
  "finance",
  "financial information",
  "financial regulation",
  "financial services",
  "gdh",
  "government id",
  "health",
  "higher education",
  "housing & rentals",
  "hr",
  "identity",
  "identity & contact",
  "location",
  "location services",
  "loyalty programs",
  "marketing",
  "non-profit organizations",
  "payments",
  "personal identification",
  "property management",
  "real estate",
  "real estate listing website",
  "real estate portal",
  "string",
  "student records",
  "taxation",
  "telecommunications",
  "tracking",
  "user authentication",
  "user profile",
];

export const legalBasisOptions = [
  {
    regulation: "DPDPA",
    articles: [
      {
        title: "Section 4(1)(a)",
        description:
          "Processing based on the free, specific, informed, unconditional, and unambiguous consent of the Data Principal.",
      },
      {
        title: "Section 7(a)",
        description:
          "Processing for the specified purpose for which the Data Principal voluntarily provided data, without indicating non-consent.",
      },

      {
        title: "Section 7(b)",
        description:
          "Processing by the State for providing subsidies, benefits, services, certificates, licenses, or permits based on prior consent or existing notified databases.",
      },

      {
        title: "Section 7(c)",
        description:
          "Processing for the performance of any function by the State under law, or in the interest of sovereignty, integrity, or security of India.",
      },
      {
        title: "Section 7(d)",
        description:
          "Processing for fulfilling any legal obligation on any person to disclose information to the State or its instrumentalities.",
      },

      {
        title: "Section 7(e)",
        description:
          "Processing for compliance with any judgment, decree, or order under Indian law, or relevant judgments/orders under foreign law.",
      },

      {
        title: "Section 7(f)",
        description:
          "Processing for responding to a medical emergency involving a threat to the life or immediate health of the Data Principal or another individual.",
      },

      {
        title: "Section 7(g)",
        description:
          "Processing for providing medical treatment or health services during an epidemic, outbreak, or other threat to public health.",
      },

      {
        title: "Section 7(h)",
        description:
          "Processing for ensuring safety or providing assistance/services during a disaster or breakdown of public order.",
      },
      {
        title: "Section 7(i)",
        description:
          "Processing for employment purposes or safeguarding the employer from loss/liability (e.g., preventing espionage, maintaining confidentiality).",
      },
    ],
  },
  {
    regulation: "GDPR",
    articles: [
      {
        title: "Art. 6(1)(a)",
        description:
          "Consent: Processing based on the data subject's explicit consent for specific purposes.",
      },
      {
        title: "Art. 6(1)(b)",
        description:
          "Contract: Processing is necessary for the performance of a contract with the data subject or to take pre-contractual steps.",
      },
      {
        title: "Art. 6(1)(c)",
        description:
          "Legal Obligation: Processing is necessary for compliance with a legal obligation to which the controller is subject.",
      },
      {
        title: "Art. 6(1)(d)",
        description:
          "Vital Interests: Processing is necessary to protect the vital interests of the data subject or another natural person.",
      },
      {
        title: "Art. 6(1)(e)",
        description:
          "Public Task: Processing is necessary for the performance of a task carried out in the public interest or in the exercise of official authority.",
      },
      {
        title: "Art. 6(1)(f)",
        description:
          "Legitimate Interests: Processing is necessary for the purposes of legitimate interests pursued by the controller or a third party, unless overridden by data subject's rights.",
      },
    ],
  },
  {
    regulation: "CCPA/CPRA",
    articles: [
      {
        title: "Â§ 1798.100(b)",
        description:
          "Notice at Collection: Data collected according to purposes disclosed in the notice provided to the consumer at or before the point of collection.",
      },
      {
        title: "Â§ 1798.100(a)(2)",
        description:
          "Purpose Limitation: Data collected for specific, explicit, legitimate purposes disclosed; not further processed incompatibly without consent.",
      },
      {
        title: "Â§ 1798.100(c)",
        description:
          "Data Minimization: Collection, use, retention, and sharing is reasonably necessary and proportionate to achieve disclosed purposes.",
      },
    ],
  },
  {
    regulation: "LGPD",
    articles: [
      {
        title: "Art. 7(I)",
        description: "Consent: Processing based on the data subject's consent.",
      },
      {
        title: "Art. 7(II)",
        description:
          "Legal/Regulatory Obligation: Processing is necessary to comply with the controller's legal or regulatory obligations.",
      },
      {
        title: "Art. 7(III)",
        description:
          "Public Administration/Policy: Processing by public administration for public policies set out in law, regulation, or contracts.",
      },
      {
        title: "Art. 7(IV)",
        description:
          "Research Studies: Processing for research studies (preferably anonymized).",
      },
      {
        title: "Art. 7(V)",
        description:
          "Contract Execution: Processing is necessary to carry out a contract with the data subject.",
      },
      {
        title: "Art. 7(VI)",
        description:
          "Exercise of Rights: Processing for the regular exercise of rights in judicial, administrative, or arbitral proceedings.",
      },
      {
        title: "Art. 7(VII)",
        description:
          "Protection of Life/Safety: Processing to protect the life or physical safety of the data subject or a third party.",
      },
      {
        title: "Art. 7(VIII)",
        description:
          "Health Protection: Processing by healthcare/sanitation professionals to safeguard a person's health.",
      },
      {
        title: "Art. 7(IX)",
        description:
          "Legitimate Interests: Processing for the legitimate interests of the controller/third party, unless overridden by data subject's rights.",
      },
      {
        title: "Art. 7(X)",
        description: "Credit Protection: Processing to protect credit ratings.",
      },
    ],
  },
  {
    regulation: "PIPEDA",
    articles: [
      {
        title: "Principle 3 / 4.3",
        description:
          "Consent: Knowledge and consent required for collection, use, or disclosure (except where inappropriate, e.g., legal/security reasons).",
      },
      {
        title: "Principle 2 / 4.2",
        description:
          "Identifying Purposes: Purposes identified by the organization before or at the time of collection.",
      },
      {
        title: "Principle 4 / 4.4",
        description:
          "Limiting Collection: Collection limited to purposes identified; collected by fair and lawful means.",
      },
      {
        title: "Principle 5 / 4.5",
        description:
          "Limiting Use/Disclosure: Used/disclosed only for identified purposes, unless consent obtained or required by law.",
      },
    ],
  },
  {
    regulation: "PIPL",
    articles: [
      {
        title: "Art. 13(1)",
        description: "Consent: Processing based on the individual's consent.",
      },
      {
        title: "Art. 13(2)",
        description:
          "Contract/HR: Necessary for concluding/performing a contract or for HR management under rules/collective contracts.",
      },
      {
        title: "Art. 13(3)",
        description:
          "Legal Duty/Obligation: Necessary for performing statutory duties or legal obligations.",
      },
      {
        title: "Art. 13(4)",
        description:
          "Public Health/Safety: Necessary to respond to public health incidents or protect life, health, and property safety in emergencies.",
      },
      {
        title: "Art. 13(5)",
        description:
          "Public Interest: Processing within reasonable scope for news reporting, public opinion supervision, etc., for public interest.",
      },
      {
        title: "Art. 13(6)",
        description:
          "Publicly Disclosed Data: Processing personal information already disclosed by the individual or otherwise legally disclosed, within a reasonable scope.",
      },
      {
        title: "Art. 13(7)",
        description:
          "Other Legal Circumstances: Other circumstances stipulated by laws and administrative regulations.",
      },
    ],
  },
  {
    regulation: "APPI",
    articles: [
      {
        title: "Art. 17",
        description:
          "Purpose Specification: Processing based on a purpose of utilization specified as much as possible.",
      },
      {
        title: "Art. 18",
        description:
          "Use Limitation: Processing limited to the scope necessary for the specified purpose (unless consent obtained or legally permitted).",
      },
      {
        title: "Art. 20(1)",
        description:
          "Proper Acquisition: Data acquired properly, not through deceit or other improper means.",
      },
      {
        title: "Art. 20(2)",
        description:
          "Sensitive Data Consent: Consent obtained for acquiring sensitive personal information (unless legally permitted exception applies).",
      },
      {
        title: "Art. 27(1)",
        description:
          "Third-Party Provision Consent: Consent obtained prior to providing personal data to a third party (unless legally permitted exception applies).",
      },
    ],
  },
  {
    regulation: "POPIA",
    articles: [
      {
        title: "Sec 11(1)(a)",
        description: "Consent: Processing based on the data subject's consent.",
      },
      {
        title: "Sec 11(1)(b)",
        description:
          "Contract: Processing necessary to carry out actions for the conclusion or performance of a contract to which the data subject is party.",
      },
      {
        title: "Sec 11(1)(c)",
        description:
          "Legal Obligation: Processing complies with an obligation imposed by law on the responsible party.",
      },
      {
        title: "Sec 11(1)(d)",
        description:
          "Data Subject Interest: Processing protects a legitimate interest of the data subject.",
      },
      {
        title: "Sec 11(1)(e)",
        description:
          "Public Law Duty: Processing necessary for the proper performance of a public law duty by a public body.",
      },
      {
        title: "Sec 11(1)(f)",
        description:
          "Legitimate Interests: Processing necessary for pursuing the legitimate interests of the responsible party or a third party to whom information is supplied.",
      },
    ],
  },
];
