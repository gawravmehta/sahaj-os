from typing import List, Optional
from pydantic import BaseModel


class DataProcessingActivity(BaseModel):
    activity_name: str
    purpose_id: str
    purpose: str
    lawful_basis: str
    data_elements: List[str]
    frequency: str
    storage_location: str


class DPDPAComplianceStatus(BaseModel):
    signed_dpa: bool
    transfer_outside_india: bool
    cross_border_mechanism: str
    breach_notification_time: str


class SecurityMeasure(BaseModel):
    measure_name: str
    description: str
    compliance_reference: str


class AuditStatus(BaseModel):
    last_audit_date: Optional[str]
    next_audit_due: Optional[str]
    audit_result: Optional[str]


class ContactPerson(BaseModel):
    name: str
    designation: str
    email: str
    phone: Optional[str]


class ContractDocument(BaseModel):
    document_name: str
    document_url: str
    signed_on: str


class CreateMyVendor(BaseModel):
    dpr_name: Optional[str] = None
    dpr_legal_name: Optional[str] = None
    dpr_logo_url: Optional[str] = None
    description: Optional[str] = None
    dpr_address: Optional[str] = None
    dpr_country: Optional[str] = None
    dpr_country_risk: Optional[str] = None
    dpr_privacy_policy: Optional[str] = None
    dpr_data_policy: Optional[str] = None
    dpr_security_policy: Optional[str] = None
    industry: Optional[str] = None
    processing_category: Optional[List[str]] = None
    data_categories: Optional[List[str]] = None
    data_processing_activity: Optional[List[DataProcessingActivity]] = None
    data_retention_policy: Optional[str] = None
    data_location: Optional[List[str]] = None
    cross_border: Optional[bool] = None
    sub_processor: Optional[bool] = None
    sub_processors: Optional[List[str]] = []
    legal_basis_of_processing: Optional[str] = None
    dpdpa_compliance_status: Optional[DPDPAComplianceStatus] = None
    security_measures: Optional[List[SecurityMeasure]] = None
    audit_status: Optional[AuditStatus] = None
    contact_person: Optional[ContactPerson] = None
    contract_documents: Optional[List[ContractDocument]] = None


class UpdateMyVendor(BaseModel):
    dpr_name: Optional[str] = None
    dpr_legal_name: Optional[str] = None
    description: Optional[str] = None
    dpr_address: Optional[str] = None
    dpr_country: Optional[str] = None
    dpr_country_risk: Optional[str] = None
    dpr_privacy_policy: Optional[str] = None
    dpr_data_policy: Optional[str] = None
    dpr_security_policy: Optional[str] = None
    industry: Optional[str] = None
    processing_category: Optional[List[str]] = None
    data_categories: Optional[List[str]] = None
    data_processing_activity: Optional[List[DataProcessingActivity]] = None
    data_retention_policy: Optional[str] = None
    data_location: Optional[List[str]] = None
    cross_border: Optional[bool] = None
    sub_processor: Optional[bool] = None
    sub_processors: Optional[List[str]] = []
    legal_basis_of_processing: Optional[str] = None
    dpdpa_compliance_status: Optional[DPDPAComplianceStatus] = None
    security_measures: Optional[List[SecurityMeasure]] = None
    audit_status: Optional[AuditStatus] = None
    contact_person: Optional[ContactPerson] = None
    contract_documents: Optional[List[ContractDocument]] = None
