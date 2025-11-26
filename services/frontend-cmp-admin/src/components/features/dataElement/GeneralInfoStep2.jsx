"use client";
import TranslationManager from "@/components/shared/TranslationManager";

const GeneralInfoStep2 = ({
  formData,
  handleInputChange,
  languagesWithoutEnglish,
}) => {
  return (
    <div className="mt-6 flex w-full max-w-lg flex-col px-3 h-full ">
      <h1 className="text-[26px]">Translations & Purposes</h1>
      <p className=" text-xs text-subHeading">
        Manage translations and assign purposes to this data element.
      </p>

      <div className="mt-4 pb-5">
        <TranslationManager
          formData={formData}
          handleInputChange={handleInputChange}
          languagesWithoutEnglish={languagesWithoutEnglish}
          inputValue={formData?.de_name}
        />
      </div>
    </div>
  );
};

export default GeneralInfoStep2;
