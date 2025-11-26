"use client";

import TranslationManager from "@/components/shared/TranslationManager";
import { languagesOptions } from "@/constants/countryOptions";
import "react-datepicker/dist/react-datepicker.css";

const CreateStep3 = ({
  formData,
  updateField,
  missingFields = [],
  wrongFields = [],
}) => {
  const languagesWithoutEnglish = languagesOptions.filter(
    (lang) => lang.value !== "en"
  );

  return (
    <div className="flex w-full max-w-lg flex-col px-3 py-6">
      <h1 className="text-[22px]">Add Translations</h1>
      <p className="mb-6 text-xs text-subHeading">
        Select a language and provide the translated text for this step.
      </p>

      <div className="flex flex-col gap-3.5 px-1 ">
      <TranslationManager
          formData={formData}
          handleInputChange={updateField}
          languagesWithoutEnglish={languagesWithoutEnglish}
          inputValue= {formData?.purpose_title}
          selectTooltipText = {"Add localized (multi-language) versions of the consent purpose details."}
          TextareaTooltipText = {"Add localized (multi-language) versions of the consent purpose details."}
          useScroll = {false}
          
        />
        
      </div>
    </div>
  );
};

export default CreateStep3;
