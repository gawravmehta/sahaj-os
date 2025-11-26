import {
  InputField,
  SelectInput,
  TagInput,
  TextareaField,
} from "@/components/ui/Inputs";
import {
  incidentTypeOptions,
  severityOptions,
  stageOptions,
} from "@/constants/breachManagementOptions";
import { apiCall } from "@/hooks/apiCall";
import React, { useEffect, useState } from "react";

const GeneralInfoStep1 = ({
  formData,
  setFormData,
  handleInputChange,
  missingFields,
}) => {
  const [assigneeOptions, setAssigneeOptions] = useState([]);
  const isFieldMissing = (fieldName) => missingFields.includes(fieldName);

  useEffect(() => {
    const fetchAssignees = async () => {
      try {
        const response = await apiCall("/auth/get-df-users");
        const formattedDocument = response.data.map((item) => ({
          value: item._id,
          label: item.email,
        }));
        setAssigneeOptions(formattedDocument);
      } catch (error) {
        console.error("Error fetching assignees:", error);
      }
    };
    fetchAssignees();
  }, []);

  return (
    <div className="mt-6 flex w-full max-w-lg flex-col px-3">
      <h1 className="text-[26px]">General Information</h1>
      <p className="mb-6 text-xs text-subHeading">
        Add basic details about the incident, like what happened, its type, and
        who is handling it.
      </p>

      <div className="flex flex-col gap-4 pb-5">
        <InputField
          required
          missingFields={missingFields}
          name="Breach Incident Name"
          label="Breach Incident Name"
          placeholder="Enter Breach Incident Name"
          value={formData.incident_name}
          onChange={(e) => handleInputChange("incident_name", e.target.value)}
          tooltipText="Give a short and clear title for this breach incident."
        />

        <div className="flex w-full justify-between gap-4">
          <div className="w-1/2">
            <SelectInput
              label="Type"
              name="incident_type"
              value={incidentTypeOptions.find(
                (opt) => opt.value === formData.incident_type
              )}
              onChange={(selectedOption) =>
                handleInputChange("incident_type", selectedOption?.value || "")
              }
              options={incidentTypeOptions}
              placeholder="Select incident type"
              error={isFieldMissing("incident_type")}
              errorMessage="Type is required"
              tooltipText="Choose the category that best matches this incident."
              required
            />
          </div>

          <div className="w-1/2">
            <SelectInput
              label="Sensitivity"
              name="incident_sensitivity"
              value={severityOptions.find(
                (opt) => opt.value === formData.incident_sensitivity
              )}
              onChange={(selectedOption) =>
                handleInputChange(
                  "incident_sensitivity",
                  selectedOption?.value || ""
                )
              }
              options={severityOptions}
              placeholder="Select sensitivity level"
              error={isFieldMissing("incident_sensitivity")}
              errorMessage="Severity is required"
              tooltipText="Select how serious or urgent the incident is."
              required
            />
          </div>
        </div>

        <TextareaField
          label="Description"
          name="description"
          value={formData.description}
          onChange={(e) => handleInputChange("description", e.target.value)}
          rows={4}
          placeholder="Write a brief description"
          error={isFieldMissing("description")}
          errorMessage="Description is required"
          tooltipText="Write a short summary of what the incident is about."
          required
        />

        <SelectInput
          label="Assignee"
          name="assignee"
          value={assigneeOptions.find((opt) => opt.value === formData.assignee)}
          onChange={(selectedOption) =>
            handleInputChange("assignee", selectedOption?.value || "")
          }
          options={assigneeOptions}
          placeholder="Select an assignee (optional)"
          tooltipText="Select the person responsible for handling this."
        />
      </div>
    </div>
  );
};

export default GeneralInfoStep1;
