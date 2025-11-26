from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Pagination(BaseModel):
    current_page: int
    data_per_page: int
    total_items: int
    total_pages: int


class LanguageCodes(str, Enum):
    eng = "eng"
    hin = "hin"
    ben = "ben"
    tel = "tel"
    mar = "mar"
    tam = "tam"
    urd = "urd"
    guj = "guj"
    kan = "kan"
    mal = "mal"
    ori = "ori"
    pan = "pan"
    asm = "asm"
    mai = "mai"
    sat = "sat"
    kas = "kas"
    nep = "nep"
    snd = "snd"
    kok = "kok"
    doi = "doi"
    mni = "mni"
    brx = "brx"
    san = "san"


class LanguageCodeEnglish(str, Enum):
    eng = "English"
    hin = "Hindi"
    ben = "Bengali"
    tel = "Telugu"
    mar = "Marathi"
    tam = "Tamil"
    urd = "Urdu"
    guj = "Gujarati"
    kan = "Kannada"
    mal = "Malayalam"
    ori = "Odia"
    pan = "Punjabi"
    asm = "Assamese"
    mai = "Maithili"
    sat = "Santali"
    kas = "Kashmiri"
    nep = "Nepali"
    snd = "Sindhi"
    kok = "Konkani"
    doi = "Dogri"
    mni = "Manipuri"
    brx = "Bodo"
    san = "Sanskrit"


class ConsentEvent(Enum):
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_VALIDATED = "CONSENT_VALIDATED"
    CONSENT_UPDATED = "CONSENT_UPDATED"
    CONSENT_RENEWED = "CONSENT_RENEWED"
    CONSENT_WITHDRAWN = "CONSENT_WITHDRAWN"
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    DATA_ERASURE_MANUAL_TRIGGERED = "DATA_ERASURE_MANUAL_TRIGGERED"
    DATA_ERASURE_RETENTION_TRIGGERED = "DATA_ERASURE_RETENTION_TRIGGERED"
    DATA_UPDATE_REQUESTED = "DATA_UPDATE_REQUESTED"
    CONSENT_AUDIT_LOG = "CONSENT_AUDIT_LOG"
    GRIEVANCE_RAISED = "GRIEVANCE_RAISED"


CONSENT_EVENTS = [
    {
        "event_name": "CONSENT_GRANTED",
        "description": "Notification that a new, valid consent artifact has been created and logged, permitting processing for a specific purpose.",
        "when_triggered": "When the Data Principal takes the explicit affirmative action (e.g., clicks 'Accept') on a compliant consent notice.",
        "why_triggered": "To establish the lawful basis for processing and create the initial Consent Artifact.",
        "action_required_by_df": "Begin data processing for the specified purpose(s) based on the new lawful basis.",
    },
    {
        "event_name": "CONSENT_VALIDATED",
        "description": "Real-time confirmation that an active consent exists and is verifiable/valid for the intended processing (the 'Green Light').",
        "when_triggered": "Every time the DF attempts to access, use, or process a Data Principal’s personal data for a specific purpose.",
        "why_triggered": "To act as a legal checkpoint for real-time compliance, ensuring the consent is active and specific.",
        "action_required_by_df": "Proceed with processing only if consent is VALID; halt otherwise.",
    },
    {
        "event_name": "CONSENT_UPDATED",
        "description": "Notification that the Data Principal has modified the scope, terms, or purposes of a previously granted consent.",
        "when_triggered": "When the Data Principal modifies the scope or details of an existing consent via the CMS.",
        "why_triggered": "To ensure the DF adjusts processing activities precisely to align with the Data Principal’s current, granular preferences.",
        "action_required_by_df": "Adjust processing activities immediately to strictly align with the modified consent.",
    },
    {
        "event_name": "CONSENT_RENEWED",
        "description": "Notification that a time-bound consent has been successfully renewed by the Data Principal.",
        "when_triggered": "When a time-bound consent is approaching expiry and the Data Principal confirms they wish to extend the processing period.",
        "why_triggered": "To maintain the lawful basis without interruption by extending the validity period of the consent artifact.",
        "action_required_by_df": "Continue processing under the renewed consent terms.",
    },
    {
        "event_name": "CONSENT_WITHDRAWN",
        "description": "Critical, real-time alert that the Data Principal has revoked their consent for one or more purposes.",
        "when_triggered": "When the Data Principal explicitly revokes consent via the CMS dashboard or a linked interface.",
        "why_triggered": "To enforce the Right to Withdraw Consent, triggering the DF's immediate obligation to cease processing.",
        "action_required_by_df": "Immediately cease all processing activities related to the withdrawn purpose(s).",
    },
    {
        "event_name": "CONSENT_EXPIRED",
        "description": "Notification that a consent period has lapsed without renewal and is no longer valid for processing.",
        "when_triggered": "When a time-bound consent reaches its pre-determined end date without being renewed.",
        "why_triggered": "To inform the DF that the lawful basis of consent has ended and processing must immediately cease.",
        "action_required_by_df": "Stop processing activities related to the expired consent.",
    },
    {
        "event_name": "DATA_ERASURE_MANUAL_TRIGGERED",
        "description": "Indicates that the Data Principal has manually requested deletion/anonymization of their data (Right to Erasure).",
        "when_triggered": "When the Data Principal directly submits a request to the CMS for deletion or anonymization.",
        "why_triggered": "To initiate the DF's process to delete or anonymize the personal data as mandated by the Data Principal's right.",
        "action_required_by_df": "Immediately delete or anonymize the data as requested by the Data Principal.",
    },
    {
        "event_name": "DATA_ERASURE_RETENTION_TRIGGERED",
        "description": "Indicates that personal data must be erased or anonymized because the retention period has expired.",
        "when_triggered": "When the original purpose for processing is no longer served, or the stated retention period has lapsed.",
        "why_triggered": "To enforce the DPDPA obligation that personal data cannot be stored indefinitely after its purpose is fulfilled.",
        "action_required_by_df": "Delete or anonymize data according to the data retention policy.",
    },
    {
        "event_name": "DATA_UPDATE_REQUESTED",
        "description": "Indicates that the Data Principal has submitted a request to update or correct their personal data.",
        "when_triggered": "When the Data Principal submits a request to the CMS to update or correct inaccuracies in their personal data.",
        "why_triggered": "To enforce the Right to Correction and Completion, compelling the DF to validate and update internal records.",
        "action_required_by_df": "Validate the request and update internal records and any active processing pipelines accordingly.",
    },
    {
        "event_name": "GRIEVANCE_RAISED",
        "description": "Notification that the Data Principal has submitted a formal grievance or complaint via the CMS/linked mechanism.",
        "when_triggered": "When a Data Principal uses the CMS or linked portal to log a formal complaint regarding data misuse or consent violation.",
        "why_triggered": "To initiate the DF's mandatory Grievance Redressal process and alert the DF's designated officer immediately.",
        "action_required_by_df": "Review and address the grievance per internal and regulatory procedures.",
    },
]
