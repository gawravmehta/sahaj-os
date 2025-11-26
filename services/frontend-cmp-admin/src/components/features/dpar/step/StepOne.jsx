"use client";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { countryOptions } from "@/constants/countryOptions";

const categoryOptions = [
  { label: "General", value: "general" },
  { label: "Marketing", value: "marketing" },
  { label: "Security", value: "security" },
  { label: "Legal", value: "legal" },
];

const StepOne = ({
  country,
  setCountry,
  category,
  setCategory,
  firstName,
  setFirstName,
  lastName,
  setLastName,
  coreIdentifier,
  setCoreIdentifier,

  secondaryIdentifier,
  setSecondaryIdentifier,
}) => {
  return (
    <div className="mx-auto w-full max-w-4xl">
      <h1 className="mb-1 text-[22px] font-semibold text-heading">
        General Information
      </h1>
      <p className="mb-6 text-xs font-light text-subHeading">
        Add basic details about the incident, like what happened, its type, and
        who is handling it.
      </p>

      <form>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-1">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <InputField
              label="First Name"
              placeholder="Enter First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />

            <InputField
              label="Last Name"
              placeholder="Enter Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
          </div>

          <InputField
            label="Core Identifier"
            placeholder="Enter Email or Mobile No."
            value={coreIdentifier}
            onChange={(e) => setCoreIdentifier(e.target.value)}
            required
          />

          <InputField
            label="Secondary Identifier "
            placeholder="Enter Email or Mobile No."
            value={secondaryIdentifier}
            onChange={(e) => setSecondaryIdentifier(e.target.value)}
          />
        </div>

        <div className="mt-3 grid grid-cols-2 gap-4">
          <SelectInput
            label="Country"
            options={countryOptions}
            value={country}
            onChange={setCountry}
            placeholder="Select Country"
            required
          />

          <SelectInput
            label="Category"
            options={categoryOptions}
            value={category}
            onChange={setCategory}
            placeholder="Select Category"
            required
          />
        </div>
      </form>
    </div>
  );
};

export default StepOne;
