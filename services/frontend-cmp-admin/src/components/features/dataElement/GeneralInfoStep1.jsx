"use client";
import {
  InputField,
  RetentionPeriodField,
  SelectInput,
  TextareaField,
} from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { sensitivityOptions, typeOptions } from "@/constants/dataElement";

const GeneralInfoStep1 = ({ formData, handleInputChange, missingFields }) => {
  return (
    <div className="mt-6 flex w-full max-w-lg flex-col px-3">
      <h1 className="text-[26px]">General Information</h1>
      <p className="mb-6 text-xs text-subHeading">
        Provide details about the data element for categorization and usage.
      </p>

      <div className="flex flex-col gap-4 pb-5">
        <InputField
          required
          missingFields={missingFields}
          name="de_name"
          label="Name"
          placeholder="Enter Data Element Name"
          value={formData.de_name}
          onChange={(e) => handleInputChange("de_name", e.target.value)}
          tooltipText="The label assigned by the organization to help understand and identify a data element easily."
        />

        <InputField
          required
          missingFields={missingFields}
          name="de_original_name"
          label="Original Name"
          placeholder="Enter Original Name"
          value={formData.de_original_name}
          onChange={(e) =>
            handleInputChange("de_original_name", e.target.value)
          }
          tooltipText="The exact name or identifier used in the database or technical system to store the data element (e.g., 'mobile_number' for mobile number)"
        />

        <TextareaField
          label="Description"
          placeholder="Write a Brief Description"
          value={formData.de_description}
          onChange={(e) => handleInputChange("de_description", e.target.value)}
          tooltipText="A brief explanation of the data element, detailing its purpose and what information it contains."
        />

        <div className="grid grid-cols-2 gap-4 items-center w-full">
          <SelectInput
            name="de_data_type"
            label="Data Type"
            placeholder="Select Data Type"
            options={typeOptions}
            value={typeOptions.find(
              (option) => option.value === formData.de_data_type
            )}
            onChange={(selected) =>
              handleInputChange("de_data_type", selected?.value || "")
            }
            required
            missingFields={missingFields}
            tooltipText="Specifies the format or kind of data stored in the element. Examples include String (text), Number (numeric values), Binary (0s and 1s), and others."
          />

          <SelectInput
            name="de_sensitivity"
            label="Sensitivity"
            placeholder="Select Sensitivity"
            options={sensitivityOptions}
            value={sensitivityOptions.find(
              (option) => option.value === formData.de_sensitivity
            )}
            onChange={(selected) =>
              handleInputChange("de_sensitivity", selected?.value || "")
            }
            required
            tooltipText="Indicates how confidential or critical the data is. It helps determine the level of protection and access controls required."
            missingFields={missingFields}
          />
        </div>

        <RetentionPeriodField
          name="de_retention_period"
          label="Retention Period"
          tooltipText="The duration for which the data will be retained, starting from the date of consent."
          missingFields={missingFields}
          placeholder="Enter Purpose Expiry Period"
          required
          valueInDays={formData.de_retention_period}
          onChange={(days) => handleInputChange("de_retention_period", days)}
        />

        <YesNoToggle
          className="w-full"
          name="is_core_identifier"
          label="Is Core Identifier?"
          value={formData.is_core_identifier}
          onChange={(_, value) =>
            handleInputChange("is_core_identifier", value)
          }
          tooltipText="If set to true, this data element is the primary identifier for the user and is used to manage their consents. Usually, the mobile number, email, or both serve as the primary identifier in most cases."
        />
      </div>
    </div>
  );
};

export default GeneralInfoStep1;
