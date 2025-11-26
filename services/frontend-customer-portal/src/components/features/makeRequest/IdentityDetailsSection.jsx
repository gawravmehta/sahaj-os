import { FaTimes } from "react-icons/fa";
import { SelectInput } from "@/components/ui/Inputs";
import {
  IDENTITY_BUTTONS,
  COUNTRY_OPTIONS,
  FORM_TEXT,
} from "@/constants/formConstants";

const IdentityDetailsSection = ({
  clickedButtons,
  handleButtonClick,
  country,
  setCountry,
}) => {
  return (
    <>
      <div className="">
        <h2 className="text-xl lg:2xl">{FORM_TEXT.IDENTITY_DETAILS}</h2>
      </div>
      <div className="flex gap-6 w-full">
        <div className="w-full sm:flex sm:flex-col gap-3 ">
          <span className="text-sm">I am</span>
          <div className="flex gap-2  text-center">
            {IDENTITY_BUTTONS.map((buttonLabel, index) => (
              <div
                key={index}
                onClick={() => handleButtonClick(buttonLabel)}
                className={`flex justify-center md:w-[62%] xl:w-[65%] items-center cursor-pointer 2xl:text-sm text-xs gap-2 rounded-full md:max-w-20 text-center px-4 md:px-1 py-1 border border-[#1D478E] ${
                  clickedButtons.includes(buttonLabel)
                    ? "bg-[#1D478E] text-white text-center"
                    : "bg-white text-[#1D478E]"
                }`}
              >
                {buttonLabel}
                {clickedButtons.includes(buttonLabel) && (
                  <FaTimes className="text-sm text-white" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="w-[48%]">
        <SelectInput
          label="Country"
          options={COUNTRY_OPTIONS}
          value={country}
          onChange={(selected) => setCountry(selected)}
          placeholder="Select country"
        />
      </div>
    </>
  );
};

export default IdentityDetailsSection;
