import {
  InputField,
  SelectInput,
  TagInput,
  TextareaField,
} from "@/components/ui/Inputs";
import Tag from "@/components/ui/Tag";
import YesNoToggle from "@/components/ui/YesNoToggle";
import {
  countryOptions,
  languagesOptions,
  statesOptions,
} from "@/constants/countryOptions";
import { activeDevices, identifiers } from "@/constants/principalManagement";
import { apiCall } from "@/hooks/apiCall";
import { useEffect, useState } from "react";

const CreateEditDp = ({
  isEdit,
  formData,
  setFormData,
  mobile,
  setMobile,
  wrongFields,
  missingFields,
  allEmails,
  allMobile,
  allOtherIdentifiers,
  tagOptions,
  setTagOptions,
  allDataElements,
  setAllDataElements,
}) => {
  const [emailError, setEmailError] = useState("");

  useEffect(() => {
    const fetchDataElements = async () => {
      try {
        const response = await apiCall(
          "/data-elements/get-all-data-element?current_page=1&data_per_page=1000&is_core_identifier=true"
        );
        if (response?.data_elements) {
          setAllDataElements(
            response.data_elements.map((el) => ({
              value: el.de_name,
              label: el.de_name,
            }))
          );
        }
      } catch (error) {
        console.error("Error fetching data elements", error);
      }
    };
    fetchDataElements();
  }, []);

  const handleSelectChange = (selectedValue, field) => {
    setFormData({ ...formData, [field]: selectedValue });
  };

  const handleEmailChange = (e) => {
    const email = e.target.value;
    setFormData({ ...formData, email });
    validateEmail(email);
  };

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
      setEmailError("Please enter a valid email address");
    } else {
      setEmailError("");
    }
  };

  const identifiersOptions = [
    ...identifiers,
    ...allDataElements.map((opt) => ({
      ...opt,
      isDisabled:
        formData?.identifiers?.some((id) =>
          allDataElements.map((el) => el.value).includes(id)
        ) && !formData?.identifiers?.includes(opt.value),
    })),
  ];

  const selectedDataElements = formData?.identifiers?.filter((id) =>
    allDataElements.map((el) => el.value).includes(id)
  );

  const capitalizeWords = (str) => {
    return str.replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <div className="mt-1 space-y-4">
      {!isEdit && (
        <>
          <InputField
            name="System ID"
            placeholder="Enter your system id Number"
            label="System ID"
            tooltipText="Unique identifier/ID of the customer in your system"
            tooltipWidth="300"
            value={formData["systemId"]}
            required={true}
            missingFields={missingFields}
            onChange={(e) =>
              setFormData({ ...formData, ["systemId"]: e.target.value })
            }
          />
        </>
      )}
      <SelectInput
        name="identifiers"
        label="Identifiers"
        options={identifiersOptions}
        value={identifiersOptions.filter((option) =>
          formData?.identifiers?.includes(option.value)
        )}
        onChange={(selected) => {
          if (selected.length <= 3) {
            handleSelectChange(
              selected.map((item) => item.value),
              "identifiers"
            );
          }
        }}
        placeholder="Select Identifiers"
        tooltipText="A unique value used to identify a user (also called the data principal). It helps in managing their data consents. Typically, this could be an email, mobile number, or both, but at least one is required."
        missingFields={missingFields}
        required={true}
        isMulti
      />

      {formData?.identifiers?.includes("email") && (
        <div>
          <InputField
            required={true}
            missingFields={missingFields}
            name="Email"
            label="Email"
            placeholder="abcd@gmail.com"
            value={formData["email"]}
            onChange={handleEmailChange}
          />

          {emailError && (
            <span className="text-sm text-red-500">{emailError}</span>
          )}

          {allEmails?.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-2">
              {allEmails?.map((email) => (
                <Tag variant="outlineBlue" key={email} label={email} />
              ))}
            </div>
          )}
        </div>
      )}

      {formData?.identifiers?.includes("mobile") && (
        <div>
          <InputField
            required
            missingFields={missingFields}
            name="Mobile"
            label="Mobile"
            placeholder="9999999999 (10 digits)"
            value={mobile ? mobile : formData["mobile"]}
            maxLength={10}
            onChange={(e) => {
              const onlyNum = e.target.value.replace(/[^0-9]/g, "");
              setMobile
                ? setMobile(onlyNum)
                : setFormData({ ...formData, ["mobile"]: onlyNum });
            }}
          />
          {allMobile?.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-2">
              {allMobile?.map((mobile) => (
                <Tag variant="outlineBlue" key={mobile} label={mobile} />
              ))}
            </div>
          )}
        </div>
      )}

      {formData?.identifiers
        ?.filter((id) => allDataElements.map((el) => el.value).includes(id))
        .map((dataElement, index) => (
          <div key={dataElement}>
            <InputField
              missingFields={missingFields}
              required
              label={capitalizeWords(dataElement)}
              name={`dp_other_identifier-${dataElement}`}
              value={formData?.dp_other_identifier?.[index] || ""}
              placeholder={`Add notes for ${dataElement}`}
              onChange={(e) => {
                const updated = [...(formData.dp_other_identifier || [])];
                updated[index] = e.target.value;
                setFormData({
                  ...formData,
                  dp_other_identifier: updated,
                });
              }}
            />
            {allOtherIdentifiers?.[index] && (
              <div className="mt-1 flex flex-wrap gap-2">
                <Tag
                  variant="outlineBlue"
                  key={allOtherIdentifiers[index]}
                  label={allOtherIdentifiers[index]}
                />
              </div>
            )}
          </div>
        ))}

      {!isEdit && (
        <>
          <SelectInput
            missingFields={missingFields}
            name="activeDevices"
            label="Active Device"
            options={activeDevices}
            value={
              activeDevices.filter((option) =>
                formData.activeDevices?.includes(option.value)
              ) || []
            }
            onChange={(selected) =>
              handleSelectChange(
                selected.map((item) => item.value),
                "activeDevices"
              )
            }
            placeholder="Select Active Device"
            tooltipText="Customer's active devices, such as mobile, laptop, desktop, etc. This helps in understanding the customer's device usage patterns."
            tooltipWidth="300"
            isMulti
          />
        </>
      )}
      <SelectInput
        name="preferredLanguage"
        label="Preferred Language"
        options={languagesOptions.map((option) => ({
          value: option.value,
          label: `${option.label} [${option.value}]`,
        }))}
        value={languagesOptions.find(
          (option) => option.value === formData.preferredLanguage
        )}
        onChange={(selected) =>
          handleSelectChange(selected?.value, "preferredLanguage")
        }
        placeholder="Select Preferred Language"
        tooltipText="Preferred language of the customer for communication and notices"
      />

      {wrongFields.some((field) => field.value === "tags") && (
        <span className="text-sm text-red-500">
          {wrongFields.find((field) => field.value === "tags")?.message}
        </span>
      )}

      <TagInput
        missingFields={missingFields}
        name="tags"
        tags={formData.dp_tags || []}
        setTags={(newTags) =>
          setFormData((prev) => ({
            ...prev,
            dp_tags: newTags,
          }))
        }
        setTagOptions={setTagOptions}
        tagOptions={tagOptions}
        label="Tags"
        placeholder="Add Tags"
        tooltipText="Used to segment or categorize data principals into different cohorts for easier management, personalized notices, language personalization, and advanced consent collection strategies."
      />

      {wrongFields.some((field) => field.value === "tags") && (
        <span className="text-sm text-red-500">
          {wrongFields.find((field) => field.value === "tags")?.message}
        </span>
      )}

      <div className="grid grid-cols-2 gap-4">
        <SelectInput
          name="country"
          label="Country"
          options={countryOptions}
          value={
            countryOptions.find((option) => option.value == formData.country) ||
            null
          }
          onChange={(selected) =>
            handleSelectChange(selected?.value, "country")
          }
          placeholder="Select Country"
          missingFields={missingFields}
          tooltipText="Select the country where the data principal is located."
        />

        <SelectInput
          name="state"
          label="State"
          options={statesOptions}
          value={
            statesOptions.find((option) => option.value === formData.state) ||
            null
          }
          onChange={(selected) => handleSelectChange(selected?.value, "state")}
          placeholder="Select States"
          missingFields={missingFields}
          tooltipText="Select the state or region within the chosen country."
        />
      </div>

      <div className="flex justify-between">
        <div>
          <YesNoToggle
            name="is_active"
            label="Is Active"
            tooltipCss={"gap-3"}
            value={formData.is_active ?? false}
            onChange={(field, value) =>
              setFormData({ ...formData, is_active: value })
            }
            tooltipText="Is the customer active?"
          />
        </div>

        <div className="">
          <YesNoToggle
            name="is_legacy"
            label="Is legacy"
            tooltipCss={"gap-3"}
            value={formData.is_legacy ?? false}
            onChange={(field, value) =>
              setFormData({ ...formData, is_legacy: value })
            }
            tooltipText="Is the customer a legacy user?"
          />
        </div>
      </div>
    </div>
  );
};

export default CreateEditDp;
