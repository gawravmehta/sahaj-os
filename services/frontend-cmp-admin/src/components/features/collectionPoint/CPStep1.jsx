"use client";

import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";

const CPStep1 = ({ formData, setFormData, missingFields, wrongFields }) => {
  return (
    <div className="flex w-full max-w-xl flex-col px-3 pb-12 pt-6">
      <h1 className="text-[28px] leading-9">General Information</h1>
      <p className="mb-6 mt-0.5 text-xs text-subHeading">
        Provide details about the collection point to ensure proper
        categorization and usage.
      </p>

      <div className="flex flex-col gap-y-4 pb-12">
        <InputField
          name="cp_name"
          label="Identifier"
          placeholder="Enter Collection Identifier"
          tooltipText="This name will be used to identify the collection point in the consent management system."
          value={formData.cp_name}
          onChange={(e) =>
            setFormData({ ...formData, cp_name: e.target.value })
          }
          required
          missingFields={missingFields}
        />

        <TextareaField
          name="cp_description"
          label="Description"
          placeholder="Enter Description"
          tooltipText="Provide a detailed description of the collection point to help internal users understand its purpose."
          value={formData.cp_description}
          onChange={(e) =>
            setFormData({ ...formData, cp_description: e.target.value })
          }
        />
        <InputField
          name="redirection_url"
          label="Redirection URL"
          placeholder="Paste Redirection URL"
          tooltipText="Provide the URL to which users will be redirected after interacting with the collection point."
          value={formData.redirection_url}
          onChange={(e) =>
            setFormData({ ...formData, redirection_url: e.target.value })
          }
          wrongFields={wrongFields}
        />
        <InputField
          name="fallback_url"
          label="Fallback URL"
          placeholder="Paste Fallback URL"
          tooltipText="Provide the URL to which users will be redirected after interacting with the collection point."
          value={formData.fallback_url}
          onChange={(e) =>
            setFormData({ ...formData, fallback_url: e.target.value })
          }
          wrongFields={wrongFields}
        />
      </div>
    </div>
  );
};

export default CPStep1;
