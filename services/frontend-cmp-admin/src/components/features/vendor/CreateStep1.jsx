import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import { countryOptions } from "@/constants/countryOptions";
import { industryOptions } from "@/constants/industryOptions";

const options = {
  risk: [
    { label: "High", value: "high" },
    { label: "Medium", value: "medium" },
    { label: "Low", value: "low" },
  ],
};

const CreateStep1 = ({
  dpr_name,
  setDpr_name,
  dpr_legal_name,
  setDpr_legal_name,
  dpr_logo_url,
  setDpr_logo_url,
  description,
  setDescription,
  dpr_address,
  setDpr_address,
  dpr_country,
  setDpr_country,
  dpr_country_risk,
  setDpr_country_risk,
  industry,
  setIndustry,
  dpr_privacy_policy,
  setDpr_privacy_policy,
  dpr_data_policy,
  setDpr_data_policy,
  dpr_security_policy,
  setDpr_security_policy,
  missingFields,
  wrongFields,
}) => {
  return (
    <div className="flex w-full max-w-lg flex-col px-3 py-6">
      <h1 className="text-[22px]">General Information</h1>
      <p className="mb-6 text-xs text-subHeading">
        Provide legal and general information about the data-handling
        organization.
      </p>
      <div className="flex flex-col space-y-3.5 px-1 pb-12">
        <InputField
          name={"dpr_logo_url"}
          label="Logo URL"
          value={dpr_logo_url}
          onChange={(e) => setDpr_logo_url(e.target.value)}
          placeholder="Enter Vendor Logo URL"
          tooltipText="The URL of the vendor's logo."
          missingFields={missingFields}
          required={true}
        />
        <InputField
          name={"dpr_name"}
          label="Name"
          value={dpr_name}
          onChange={(e) => setDpr_name(e.target.value)}
          placeholder="Enter Vendor Name"
          tooltipText="The commonly used name of the data principal.
"
          missingFields={missingFields}
          required={true}
        />
        <InputField
          name={"description"}
          label="Legal Name"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter Vendor Legal Name"
          tooltipText="Official name as per legal documents."
          missingFields={missingFields}
        />
        <TextareaField
          name={"dpr_legal_name"}
          label="Description"
          value={dpr_legal_name}
          className="-mb-[7px]"
          onChange={(e) => setDpr_legal_name(e.target.value)}
          placeholder="Write a Brief Description"
          tooltipText="A short description of the organization's core function."
          missingFields={missingFields}
        />
        <TextareaField
          name={"dpr_address"}
          label="Address"
          value={dpr_address}
          className="-mb-[7px]"
          onChange={(e) => setDpr_address(e.target.value)}
          placeholder="Write Vendor Address"
          tooltipText="Full physical address of the organization.
"
          missingFields={missingFields}
        />
        <div className="flex w-full gap-5">
          <div className="w-1/2">
            <SelectInput
              name={"dpr_country"}
              label="Country"
              tooltipText="The country where the organization is legally based.
"
              value={countryOptions.filter((item) => item.value == dpr_country)}
              onChange={(selectedOption) =>
                setDpr_country(selectedOption.value)
              }
              options={countryOptions}
              placeholder="Select Category"
              className="w-full"
              missingFields={missingFields}
            />
          </div>

          <div className="w-1/2">
            <SelectInput
              name={"dpr_country_risk"}
              label="Risk"
              tooltipText="Risk level for cross-border transfer.
"
              value={options.risk.filter(
                (item) => item.value === dpr_country_risk
              )}
              onChange={(selectedOption) =>
                setDpr_country_risk(selectedOption.value)
              }
              options={options.risk}
              placeholder="Select DPAR Risk Level"
              className="w-full"
            />
          </div>
        </div>
        <SelectInput
          name="industry"
          label="Industry"
          tooltipText="Business sector of the organization.
"
          value={industry ? { value: industry, label: industry } : null}
          onChange={(selectedOption) =>
            setIndustry(selectedOption?.value || "")
          }
          options={Object.keys(industryOptions).map((industry) => ({
            value: industry,
            label: industry,
          }))}
          placeholder="Select Scope"
          missingFields={missingFields}
        />
        <InputField
          name={"dpr_privacy_policy"}
          label="Privacy Policy URL"
          value={dpr_privacy_policy}
          onChange={(e) => setDpr_privacy_policy(e.target.value)}
          placeholder="Paste Link"
          tooltipText="Link to the privacy policy."
          missingFields={missingFields}
        />
        <InputField
          name={"dpr_data_policy"}
          label="Data Policy URL"
          value={dpr_data_policy}
          onChange={(e) => setDpr_data_policy(e.target.value)}
          placeholder="Paste Link"
          tooltipText="Link to data processing policy.
"
          missingFields={missingFields}
        />
        <InputField
          name={"dpr_security_policy"}
          label="Security Policy URL"
          value={dpr_security_policy}
          onChange={(e) => setDpr_security_policy(e.target.value)}
          placeholder="Paste Link"
          tooltipText="Link to information security policy.
"
          missingFields={missingFields}
        />
      </div>
    </div>
  );
};

export default CreateStep1;
