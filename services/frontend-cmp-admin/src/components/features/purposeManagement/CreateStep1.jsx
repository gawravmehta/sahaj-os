"use client";

import React from "react";
import {
  InputField,
  RetentionPeriodField,
  SelectInput,
  TextareaField,
} from "@/components/ui/Inputs";
import { options } from "@/constants/purposeManagement";
import YesNoToggle from "@/components/ui/YesNoToggle";

const CreateStep1 = ({
  formData,
  updateField,
  missingFields = [],
  wrongFields = [],
}) => {
  return (
    <div className="flex w-full max-w-lg flex-col px-3 py-6">
      <h1 className="text-[22px]">General Information</h1>
      <p className="mb-6 text-xs text-subHeading">
        Provide detailed information about the data element to ensure accurate
        categorization and usage.
      </p>

      <div className="flex flex-col gap-3.5 px-1 pb-12">
        <SelectInput
          name="purpose_category"
          label="Purpose Category"
          tooltipText="Select the main category that best describes the purpose of data collection."
          options={options.purpose_category}
          value={
            formData.purpose_category
              ? options.purpose_category.find(
                  (item) => item.value === formData.purpose_category
                )
              : null
          }
          placeholder="Select Purpose Category"
          onChange={(opt) => {
            updateField("purpose_category", opt ? opt.value : null);
            updateField("purpose_sub_category", null);
          }}
        />

        <SelectInput
          name="purpose_sub_category"
          label="Purpose Sub Category"
          placeholder="Select Purpose Sub Category"
          tooltipText="Select a more specific sub-category that further defines the purpose."
          options={
            formData.purpose_category
              ? options.purpose_sub_category[formData.purpose_category]
              : []
          }
          value={
            formData.purpose_sub_category
              ? options.purpose_sub_category[formData.purpose_category]?.find(
                  (item) => item.value === formData.purpose_sub_category
                )
              : null
          }
          onChange={(opt) =>
            updateField("purpose_sub_category", opt ? opt.value : null)
          }
          isDisabled={!formData.purpose_category}
        />

        <InputField
          name="purpose_title"
          label="Consent Statement"
          value={formData.purpose_title}
          onChange={(e) => updateField("purpose_title", e.target.value)}
          placeholder="Enter Consent Statement"
          tooltipText="This is the title of the purpose for which you are collecting data."
          required
          missingFields={missingFields}
        />

        <TextareaField
          name="purpose_description"
          label="Description"
          value={formData.purpose_description}
          onChange={(e) => updateField("purpose_description", e.target.value)}
          placeholder="Write a Brief Description"
          tooltipText="Describe the purpose in detail along with its intended use."
          missingFields={missingFields}
        />

        <div className="flex w-full gap-5">
          <div className="w-1/2">
            <SelectInput
              name="review_frequency"
              label="Review Frequency"
              tooltipText="Select how often this purpose should be reviewed."
              options={options.frequency}
              value={
                formData.review_frequency
                  ? options.frequency.find(
                      (item) => item.value === formData.review_frequency
                    )
                  : null
              }
              onChange={(opt) =>
                updateField("review_frequency", opt ? opt.value : null)
              }
              placeholder="Select frequency"
              required
              missingFields={missingFields}
            />
          </div>

          <div className="w-1/2">
            <SelectInput
              name="purpose_priority"
              label="Priority"
              tooltipText="Select the priority level for this purpose."
              options={options.priority}
              value={
                formData.purpose_priority
                  ? options.priority.find(
                      (item) => item.value === formData.purpose_priority
                    )
                  : null
              }
              onChange={(opt) =>
                updateField("purpose_priority", opt ? opt.value : null)
              }
              placeholder="Select level"
              required
              missingFields={missingFields}
            />
          </div>
        </div>

        <RetentionPeriodField
          name="consent_time_period"
          label="Consent Expiry Period"
          tooltipText="The length of time for which the user’s consent is deemed legally valid."
          missingFields={missingFields}
          placeholder="Enter Consent Expiry Period"
          required
          valueInDays={formData.consent_time_period}
          onChange={(day) => updateField("consent_time_period", day, "")}
        />

        <div className="w-1/2 mb-4">
          <YesNoToggle
            name="reconsent"
            label="Is Reconsent Required?"
            tooltipText="Select Yes if users should reconsent after the consent expiry period."
            value={formData.reconsent}
            onChange={(field, value) => updateField("reconsent", value)}
          />
        </div>
      </div>
    </div>
  );
};

export default CreateStep1;
