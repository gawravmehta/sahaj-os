import { useState } from "react";
import { FiPhone } from "react-icons/fi";
import { GoMail, GoPlus } from "react-icons/go";
import { SubProcessorAccordion } from "./SubProcessorAccordion";
import { documentFields, auditResultOptions } from "@/constants/vendorOptions";
import {
  DatePickerField,
  InputField,
  SelectInput,
  TextareaField,
  Tooltip,
} from "@/components/ui/Inputs";
import Button from "@/components/ui/Button";

const CreateStep3 = ({
  security_measures,
  setSecurity_measures,
  audit_status,
  setAudit_status,
  contact_person,
  setContact_person,
  contract_documents,
  setContract_documents,
  missingFields,
  wrongFields,
}) => {
  const [processors, setProcessors] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showSubProcessorForm, setShowSubProcessorForm] = useState(false);
  const [documentsFormData, setDocumentsFormData] = useState({
    document_name: "",
    document_url: "",
    signed_on: "",
  });

  const contactDesignationOptions = [
    { label: "Data Protection Officer (DPO)", value: "DPO" },
    { label: "Chief Information Security Officer (CISO)", value: "CISO" },
    { label: "Legal Counsel", value: "Legal Counsel" },
    { label: "Compliance Manager", value: "Compliance Manager" },
    { label: "IT Manager", value: "IT Manager" },
    { label: "Director", value: "Director" },
    { label: "Other", value: "Other" },
  ];

  return (
    <div className="flex w-full max-w-lg flex-col px-3 pb-2 pt-6">
      <h1 className="text-[22px]">Security, Audit & Contact</h1>
      <p className="mb-6 text-xs text-subHeading">
        Details security measures, audit status, and key contacts for
        accountability and compliance.
      </p>
      <div className="flex flex-col gap-3.5 pb-10">
        <InputField
          name="name"
          label="Security Measure Name"
          value={security_measures?.measure_name}
          onChange={(e) =>
            setSecurity_measures({
              ...security_measures,
              measure_name: e.target.value,
            })
          }
          placeholder="Enter Security Measure Name"
          tooltipText="Title of the security measure.
r"
          missingFields={missingFields}
        />
        <TextareaField
          name="purpose"
          label="Security Description"
          value={security_measures?.description}
          onChange={(e) =>
            setSecurity_measures({
              ...security_measures,
              description: e.target.value,
            })
          }
          placeholder="Write a Security Brief Description "
          tooltipText="What the security measure does."
          className="h-20 -mb-2"
          missingFields={missingFields}
        />
        <InputField
          name="name"
          label="Compliance Reference"
          className=""
          value={security_measures?.compliance_reference}
          onChange={(e) =>
            setSecurity_measures({
              ...security_measures,
              compliance_reference: e.target.value,
            })
          }
          placeholder="Enter Compliance Reference"
          tooltipText="Standard or certification for compliance.
"
          missingFields={missingFields}
        />
        <div className="flex w-full gap-5">
          <DatePickerField
            name="last_audit_date"
            label="Last Audit Date"
            placeholder="Select Last Audit Data"
            tooltipText="Date of last data protection audit.
"
            selected={audit_status.last_audit_date}
            onChange={(date) =>
              setAudit_status({
                ...audit_status,
                last_audit_date: date,
              })
            }
            maxDate={audit_status.next_audit_due || undefined}
            missingFields={missingFields}
            wrongFields={wrongFields}
          />
          <DatePickerField
            name="next_audit_due"
            label="Next Audit Due"
            placeholder="Select Next Audit Date"
            tooltipText="Date by which next audit is planned.
"
            selected={audit_status.next_audit_due}
            onChange={(date) =>
              setAudit_status({
                ...audit_status,
                next_audit_due: date,
              })
            }
            minDate={audit_status.last_audit_date || undefined}
            missingFields={missingFields}
            wrongFields={wrongFields}
          />
        </div>
        <SelectInput
          name="dpr_country_risk"
          label="Audit Result"
          tooltipText="Status of last audit.
"
          value={
            auditResultOptions.find(
              (item) => item.value == audit_status.audit_result
            ) || null
          }
          onChange={(selectedOption) =>
            setAudit_status((prev) => ({
              ...prev,
              audit_result: selectedOption?.value || "",
            }))
          }
          options={auditResultOptions}
          placeholder="Select Audit Result"
          className="w-full"
        />
        <InputField
          name="name"
          label="Contact Name"
          value={contact_person.name}
          onChange={(e) =>
            setContact_person({
              ...contact_person,
              name: e.target.value,
            })
          }
          placeholder="Enter Contact Name"
          tooltipText="Full name of responsible person.
"
          missingFields={missingFields}
        />
        <SelectInput
          name="contact_designation"
          label="Contact Designation"
          tooltipText="Role of the contact person."
          value={
            contactDesignationOptions.find(
              (item) => item.value === contact_person.designation
            ) || null
          }
          onChange={(selectedOption) =>
            setContact_person((prev) => ({
              ...prev,
              designation: selectedOption?.value || "",
            }))
          }
          options={contactDesignationOptions}
          placeholder="Select Designation"
          className="w-full"
        />
        <div className="flex w-full gap-5">
          <div className="w-1/2">
            <div className="relative">
              <InputField
                name="name"
                label="Contact Email"
                type="email"
                value={contact_person.email}
                onChange={(e) =>
                  setContact_person({
                    ...contact_person,
                    email: e.target.value,
                  })
                }
                placeholder="Enter Contact Email"
                tooltipText="Email of the contact person.
"
                missingFields={missingFields}
                className="pr-8"
              />
              <GoMail
                className="absolute right-2 top-[35px] cursor-pointer font-bold text-placeholder"
                size={19}
              />
            </div>
          </div>
          <div className="w-1/2">
            <div className="relative">
              <InputField
                name="name"
                label="Contact Phone"
                value={contact_person.phone}
                onChange={(e) => {
                  const onlyNum = e.target.value.replace(/[^0-9]/g, "");
                  setContact_person({
                    ...contact_person,
                    phone: onlyNum,
                  });
                }}
                placeholder="Enter Contact Phone"
                tooltipText="Mobile or landline contact number.
"
                missingFields={missingFields}
                maxLength={10}
                className="pr-8"
              />
              <FiPhone
                className="absolute right-2 top-[35px] cursor-pointer font-bold text-placeholder"
                size={19}
              />
            </div>
          </div>
        </div>
        <>
          <div className="flex items-center justify-between">
            <div className="flex justify-between">
              <span className="flex items-center gap-1 text-sm text-heading">
                Add Contract Documents
              </span>
              <Tooltip tooltipWidth={"300"} />
            </div>

            <Button
              variant="secondary"
              className="h-7 text-xs"
              onClick={() => setShowSubProcessorForm(true)}
            >
              <GoPlus size={20} /> Documents
            </Button>
          </div>

          {showSubProcessorForm && (
            <div className="space-y-3.5">
              <InputField
                name="name"
                label="Document Name"
                value={documentsFormData.document_name}
                onChange={(e) =>
                  setDocumentsFormData({
                    ...documentsFormData,
                    document_name: e.target.value,
                  })
                }
                placeholder="Enter Document Name"
                tooltipText="Enter the official name or title of the contract document (e.g., Data Processing Agreement).
"
                missingFields={missingFields}
              />
              <InputField
                name="name"
                label="Document URL"
                value={documentsFormData.document_url}
                onChange={(e) =>
                  setDocumentsFormData({
                    ...documentsFormData,
                    document_url: e.target.value,
                  })
                }
                placeholder="Paste Link"
                tooltipText="Provide the secure link or storage path where the signed contract document is available."
                missingFields={missingFields}
              />
              <InputField
                name="name"
                label="Signed On"
                value={documentsFormData.signed_on}
                onChange={(e) =>
                  setDocumentsFormData({
                    ...documentsFormData,
                    signed_on: e.target.value,
                  })
                }
                placeholder="Enter Signed on"
                tooltipText="Select the date on which the contract was officially signed by both parties."
                missingFields={missingFields}
              />

              <div className="mt-3 flex justify-end gap-4">
                <Button
                  variant="cancel"
                  className="h-7 text-xs"
                  onClick={() => setShowSubProcessorForm(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="secondary"
                  className="h-7 text-xs"
                  onClick={() => {
                    setContract_documents([
                      ...contract_documents,
                      documentsFormData,
                    ]);
                    setDocumentsFormData({
                      name: "",
                      documentURL: "",
                      signedOn: "",
                    });
                    setShowSubProcessorForm(false);
                  }}
                >
                  Add
                </Button>
              </div>
            </div>
          )}
        </>
        <SubProcessorAccordion
          subProcessors={contract_documents}
          setSubProcessors={setContract_documents}
          fields={documentFields}
        />
      </div>
    </div>
  );
};

export default CreateStep3;
