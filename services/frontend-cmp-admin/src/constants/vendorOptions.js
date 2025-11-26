export const dataCategoryOptions = [
  { value: "pii", label: "Personally Identifiable Information (PII)" },
  { value: "financial_data", label: "Financial Data" },
  { value: "health_medical_data", label: "Health and Medical Data" },
  { value: "biometric_data", label: "Biometric Data" },
  { value: "government_identifiers", label: "Government Identifiers" },
  { value: "contact_information", label: "Contact Information" },
  { value: "demographic_information", label: "Demographic Information" },
  { value: "employment_data", label: "Employment Data" },
  { value: "location_data", label: "Location Data" },
  { value: "online_identifiers", label: "Online Identifiers and Tracking" },
  { value: "behavioral_usage_data", label: "Behavioral and Usage Data" },
  { value: "communication_data", label: "Communication Data" },
  {
    value: "social_media_profiles",
    label: "Social Media and Public Profile Data",
  },
  { value: "educational_data", label: "Educational Data" },
  { value: "sensitive_personal_data", label: "Sensitive Personal Data" },
];

export const processingCategoryOptions = [
  { value: "data_collection", label: "Data Collection" },
  { value: "data_storage", label: "Data Storage" },
  { value: "data_analysis", label: "Data Analysis" },
  { value: "data_sharing", label: "Data Sharing" },
  { value: "data_hosting", label: "Data Hosting" },
  { value: "data_profiling", label: "Data Profiling" },
  { value: "data_backup_recovery", label: "Data Backup/Recovery" },
  { value: "marketing_advertising", label: "Marketing/Advertising" },
  { value: "customer_support", label: "Customer Support" },
  { value: "hr_payroll_processing", label: "HR/Payroll Processing" },
  { value: "payment_processing", label: "Payment Processing" },
  { value: "cloud_infrastructure", label: "Cloud Infrastructure" },
  { value: "analytics_services", label: "Analytics Services" },
  { value: "identity_verification", label: "Identity Verification" },
];

export const lawfulBasisOptions = [
  { value: "consent", label: "Consent" },
  { value: "contractual_obligation", label: "Contractual Obligation" },
  { value: "legal_obligation", label: "Legal Obligation" },
  { value: "vital_interests", label: "Vital Interests" },
  { value: "public_task", label: "Public Task" },
  { value: "legitimate_interests", label: "Legitimate Interests" },
  {
    value: "legal_requirement_dpdpa",
    label: "Legal Requirement under DPDPA",
  },
];

export const frequencyOptions = [
  { value: "one_time", label: "One-time" },
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "quarterly", label: "Quarterly" },
  { value: "annually", label: "Annually" },
  { value: "on_demand", label: "On Demand" },
  { value: "continuous_real_time", label: "Continuous / Real-Time" },
];

export const crossBorderMechanismOptions = [
  {
    value: "standard_contractual_clauses (SCCs)",
    label: "Standard Contractual Clauses (SCCs)",
  },
  {
    value: "binding_corporate_rules(bcr)",
    label: "Binding Corporate Rules (BCRs)",
  },
  {
    value: "adequacy_decision_by_government",
    label: "Adequacy Decision by Government",
  },
  {
    value: "informed_consent_from_data_principal",
    label: "Informed Consent from Data Principal",
  },
  {
    value: "not_applicable(domestic only)",
    label: "Not Applicable (Domestic Only)",
  },
  {
    value: "govt_approved_contracts(dpdpa)",
    label: "Government Approved Contracts (DPDPA)",
  },
  { value: "dpa_authorization", label: "Explicit Authorization by DPA" },
];

export const documentFields = [
  { key: "document_name", label: "Document Name" },
  { key: "document_url", label: "Document URL" },
  { key: "signed_on", label: "Signed On" },
];

export const auditResultOptions = [
  { value: "compliant", label: "Compliant" },
  { value: "partially_compliant", label: "Partially Compliant" },
  { value: "non_compliant", label: "Non-Compliant" },
  { value: "audit_pending", label: "Audit Pending" },
  { value: "not_audited_yet", label: "Not Audited Yet" },
  { value: "under_review", label: "Under Review" },
  { value: "remediation_in_progress", label: "Remediation in Progress" },
];
