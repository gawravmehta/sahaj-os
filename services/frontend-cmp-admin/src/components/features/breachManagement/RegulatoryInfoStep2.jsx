import {
  DatePickerField,
  InputField,
  SelectInput,
} from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import {
  authorityOptions,
  complianceOptions,
} from "@/constants/breachManagementOptions";
import React from "react";

const RegulatoryInfoStep2 = ({
  formData,
  setFormData,
  handleInputChange,
  missingFields,
}) => {
  return (
    <div className="w-[480px] p-4">
      <h2 className="font-lato text-[22px] text-[#000000]">
        Timeline & Compliance
      </h2>
      <p className="text-[12px] text-[#000000] opacity-70">
        Enter key dates and check if any reporting or legal rules apply to this
        incident.
      </p>

      <div className="mt-2 flex flex-col space-y-4 pb-6">
        <div className="flex justify-between gap-4">
          <div className="w-1/2">
            <DatePickerField
              name="date_occurred"
              label="Occurred"
              placeholder="Select occurrence date"
              selected={formData.date_occurred}
              onChange={(date) => handleInputChange("date_occurred", date)}
              required
              missingFields={missingFields}
            />
          </div>

          <div className="w-1/2">
            <DatePickerField
              name="date_discovered"
              label="Discovered"
              placeholder="Select discovery date"
              selected={formData.date_discovered}
              onChange={(date) => handleInputChange("date_discovered", date)}
              required
              missingFields={missingFields}
            />
          </div>
        </div>

        <div className="flex justify-between">
          <div className="w-[48%]">
            <DatePickerField
              name="deadline"
              label="Deadline"
              placeholder="Select deadline date"
              selected={formData.deadline}
              onChange={(date) => handleInputChange("deadline", date)}
              required
              missingFields={missingFields}
            />
          </div>
        </div>

        <YesNoToggle
          label="Regulatory Reported"
          value={formData.regulatory_reported}
          onChange={() =>
            setFormData((prev) => ({
              ...prev,
              regulatory_reported: !prev.regulatory_reported,
            }))
          }
          tooltipText="Was this reported to a regulatory body?"
          tooltipCss={"gap-3"}
        />

        {formData.regulatory_reported && (
          <div className="flex justify-between gap-4">
            <div className="w-1/2">
              <DatePickerField
                name="regulatory_reported_date"
                label="Regulatory Reported Date"
                placeholder="Select report date"
                selected={formData.regulatory_reported_date}
                onChange={(date) =>
                  handleInputChange("regulatory_reported_date", date)
                }
                required
                missingFields={missingFields}
              />
            </div>
            <div className="w-1/2">
              <SelectInput
                label="Regulatory Authority"
                value={authorityOptions.find(
                  (opt) => opt.value === formData.regulatory_authority
                )}
                onChange={(selected) =>
                  handleInputChange(
                    "regulatory_authority",
                    selected?.value || ""
                  )
                }
                options={authorityOptions}
                tooltipText="Name of the authority this was reported to."
              />
            </div>
          </div>
        )}

        <SelectInput
          label="Compliance Standard"
          value={complianceOptions.find(
            (opt) => opt.value === formData.compliance_standard
          )}
          onChange={(selected) =>
            handleInputChange("compliance_standard", selected?.value || "")
          }
          options={complianceOptions}
          tooltipText="Mention the rule or law this incident is related to (e.g., DPDPA)."
        />

        <div className="flex justify-between gap-5">
          <div className="w-1/2">
            <YesNoToggle
              label="Notification Needed"
              value={formData.notification_needed}
              onChange={() =>
                handleInputChange(
                  "notification_needed",
                  !formData.notification_needed
                )
              }
              tooltipText="Is it required to notify anyone (e.g., users, govt.)?"
              tooltipCss={"gap-3"}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegulatoryInfoStep2;
