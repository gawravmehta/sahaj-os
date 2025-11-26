import { InputField } from "@/components/ui/Inputs";
import { FORM_TEXT } from "@/constants/formConstants";

const PersonalInfoSection = ({ formData, handleChange, errors }) => {
  return (
    <>
      <h2 className="text-xl lg:2xl">{FORM_TEXT.PERSONAL_INFO}</h2>
      <div className="sm:flex gap-6 w-full">
        <div className="w-1/2">
          <InputField
            label="First Name"
            name="firstName"
            placeholder="First Name"
            value={formData.firstName}
            onChange={handleChange}
            className=""
            tooltipText="Your email address"
            required
            error={errors.firstName}
          />
        </div>
        <div className="w-1/2">
          <InputField
            label="Last Name"
            name="lastName"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            tooltipText="Your email address"
          />
        </div>
      </div>

      <div className="sm:flex justify-between gap-6 w-full">
        <div className="w-1/2">
          <InputField
            label="Core Identifier"
            name="coreIdentifier"
            placeholder="Core Identifier"
            type="coreIdentifier"
            pattern="\d*"
            maxLength={10}
            value={formData.coreIdentifier}
            onChange={handleChange}
            tooltipText="Your email address"
          />
        </div>
        <div className="w-1/2">
          <InputField
            label="Secondary Identifier"
            name="secondaryIdentifier"
            placeholder="Secondary Identifier"
            type="secondaryIdentifier"
            value={formData.secondaryIdentifier}
            onChange={handleChange}
            tooltipText="Your email address"
          />
        </div>
      </div>
    </>
  );
};

export default PersonalInfoSection;
