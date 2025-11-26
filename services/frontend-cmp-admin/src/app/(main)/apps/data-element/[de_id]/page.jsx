"use client";

import Header from "@/components/ui/Header";
import Stepper from "@/components/ui/Stepper";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import { useRouter, useSearchParams } from "next/navigation";
import { use, useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";

import GeneralInfoStep1 from "@/components/features/dataElement/GeneralInfoStep1";
import GeneralInfoStep2 from "@/components/features/dataElement/GeneralInfoStep2";
import { FaArrowRight } from "react-icons/fa6";
import MissingTranslationsModal from "@/components/shared/modals/MissingTranslationsModal";
import { getLanguageLabel } from "@/utils/helperFunctions";

const Page = ({ params }) => {
  const { de_id: elementId } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();

  const [formData, setFormData] = useState({
    de_name: "",
    de_description: "",
    de_original_name: "",
    de_data_type: "",
    de_sensitivity: "",
    is_core_identifier: false,
    de_retention_period: "",
    translations: {},
  });

  const [showModal, setShowModal] = useState(false);
  const [missingTranslation, setMissingTranslation] = useState([]);

  const [originalData, setOriginalData] = useState(null);
  const [missingFields, setMissingFields] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(
    parseInt(searchParams.get("activeTab")) || 1
  );

  const isCreate = elementId === "create";

  const handleTabChange = (tabId) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("activeTab", tabId);
    router.push(`?${params.toString()}`, { shallow: true });
  };

  useEffect(() => {
    if (!isCreate) {
      getOneDataElement();
    }
  }, []);

  const getOneDataElement = async () => {
    try {
      const response = await apiCall(
        `/data-elements/get-data-element/${elementId}`
      );
      setFormData(response || {});
      setOriginalData(response || {});
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleDataChange = useCallback((field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const validateStep1 = () => {
    const required = [
      "de_name",
      "de_original_name",
      "de_data_type",
      "de_sensitivity",
      "de_retention_period",
    ];
    const missing = required.filter(
      (f) =>
        !formData[f] || (typeof formData[f] === "string" && !formData[f].trim())
    );
    setMissingFields(missing);
    return missing.length === 0;
  };

 
  const handleSaveOrPublish = async (action) => {
    const allLanguages = [
      "hin",
      "asm",
      "ben",
      "brx",
      "guj",
      "kan",
      "kas",
      "kok",
      "mai",
      "mal",
      "mar",
      "mni",
      "nep",
      "ori",
      "pan",
      "san",
      "sat",
      "snd",
      "tam",
      "tel",
      "urd",
    ];

    let missing = [];

    if (action === "publish") {
      if (formData.translations) {
        allLanguages.forEach((langCode) => {
          const value = formData.translations?.[langCode];
          if (!value || (typeof value === "string" && !value.trim())) {
            const langLabel = getLanguageLabel(langCode);
            missing.push(langLabel);
          }
        });
      } else {
        missing = allLanguages.map((langCode) => getLanguageLabel(langCode));
      }

      if (missing.length > 0) {
        setMissingTranslation(missing);
        setShowModal(true);
        return;
      }
    }

    try {
      setLoading(true);

      if (isCreate) {
        const created = await apiCall("/data-elements/create-data-element", {
          method: "POST",
          data: formData,
        });

        const newId = created?.id || created?.de_id;
        if (!newId) throw new Error("Failed to create Data Element");

        if (action === "publish") {
          await apiCall(
            `/data-elements/publish-data-element/${encodeURIComponent(newId)}`,
            { method: "PATCH" }
          );
          toast.success("Data Element Created & Published Successfully");
        } else {
          toast.success("Data Element Drafted Successfully");
        }
      } else {
        if (formData?.translations?.eng) {
          delete formData.translations.eng;
        }

        const updatedFields = getUpdatedFields(originalData, formData);

        if (Object.keys(updatedFields).length > 0) {
          await apiCall(`/data-elements/update-data-element/${elementId}`, {
            method: "PATCH",
            data: updatedFields,
          });
          setOriginalData({ ...originalData, ...updatedFields });
        }

        if (action === "publish") {
          await apiCall(
            `/data-elements/publish-data-element/${encodeURIComponent(
              elementId
            )}`,
            { method: "PATCH" }
          );
          toast.success("Data Element Updated & Published Successfully");
        } else {
          toast.success("Draft Saved Successfully");
        }
      }

      router.push("/apps/data-element");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleNextStep = () => {
    if (!validateStep1()) {
      toast.error("Please fill in all required fields");
      return;
    }
    setActiveStep(2);
    handleTabChange(2);
  };

  const handlePrevStep = () => {
    if (activeStep > 1) {
      setActiveStep(activeStep - 1);
      handleTabChange(activeStep - 1);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/data-element/${
      isCreate ? "create" : formData.de_name || elementId
    }`,
    skip: "/apps",
  };

  return (
    <div className="flex h-full flex-col justify-between">
      <Header
        title={
          isCreate
            ? "Create a Data Element"
            : `Edit ${formData.de_name || "Data Element"}`
        }
        breadcrumbsProps={breadcrumbsProps}
      />

      <Stepper
        steps={["General Info", "Translations & Purposes"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
        className="max-w-xl"
      />

      <div className="flex h-[calc(100vh-238px)] w-full justify-center overflow-auto custom-scrollbar pb-5">
        {activeStep === 1 && (
          <GeneralInfoStep1
            formData={formData}
            setFormData={setFormData}
            handleInputChange={handleDataChange}
            missingFields={missingFields}
          />
        )}
        {activeStep === 2 && (
          <GeneralInfoStep2
            formData={formData}
            handleInputChange={handleDataChange}
            languagesWithoutEnglish={require("@/constants/countryOptions").languagesOptions.filter(
              (lang) => lang.value !== "en"
            )}
          />
        )}

        {showModal && (
          <MissingTranslationsModal
            missing={missingTranslation}
            onClose={() => setShowModal(false)}
            module="Data Element"
            onSaveDraft={() => handleSaveOrPublish("draft")}
          />
        )}
      </div>

      <StickyFooterActions
        showCancel={activeStep === 1}
        onCancelHref="/apps/data-element"
        showBack={activeStep === 2}
        onBack={handlePrevStep}
        showSaveAsDraft={true}
        onSaveAsDraft={() => handleSaveOrPublish("draft")}
        showSubmit={true}
        onSubmit={
          activeStep === 1
            ? handleNextStep
            : () => handleSaveOrPublish("publish")
        }
        submitLabel={activeStep === 1 ? "Next" : "Publish"}
        loading={loading}
        className="mt-10 py-4 shadow-xl"
      >
        {activeStep == 1 && <FaArrowRight className="text-[12px]" />}
      </StickyFooterActions>
    </div>
  );
};

export default Page;
