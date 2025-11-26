"use client";

import CreateStep1 from "@/components/features/purposeManagement/CreateStep1";
import CreateStep2 from "@/components/features/purposeManagement/CreateStep2";
import CreateStep3 from "@/components/features/purposeManagement/CreateStep3";
import MissingTranslationsModal from "@/components/shared/modals/MissingTranslationsModal";
import Header from "@/components/ui/Header";
import Stepper from "@/components/ui/Stepper";
import StickyFooterActions from "@/components/ui/StickyFooterActions.jsx";
import { apiCall } from "@/hooks/apiCall.jsx";
import { getErrorMessage } from "@/utils/errorHandler.jsx";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import { getLanguageLabel, isValidObjectId } from "@/utils/helperFunctions";
import { useRouter, useSearchParams } from "next/navigation";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FaArrowRight } from "react-icons/fa";

const Page = ({ params }) => {
  const { create: purposeId } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();

  const [formData, setFormData] = useState({
    purpose_title: "",
    purpose_description: "",
    purpose_priority: "high",
    review_frequency: "quarterly",
    consent_time_period: 0,
    reconsent: false,
    data_elements: [],
    translations: {},
  });

  const [missingFields, setMissingFields] = useState([]);
  const [originalData, setOriginalData] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);
  const [activeStep, setActiveStep] = useState(
    parseInt(searchParams.get("activeTab")) || 1
  );
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const updateField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePrevStep = () => {
    if (activeStep > 1) handleTabChange(activeStep - 1);
  };

  const handleTabChange = (tabId) => {
    setActiveStep(tabId);
    const params = new URLSearchParams(searchParams.toString());
    params.set("activeTab", tabId);
    router.push(`?${params.toString()}`, undefined, { shallow: true });
  };

  const breadcrumbsProps = {
    path: `/apps/purpose-management/${
      isValidObjectId(purposeId) ? "Update" : "Create"
    }`,
    skip: "/apps",
  };

  useEffect(() => {
    if (isValidObjectId(purposeId)) {
      fetchData();
    }
  }, [purposeId]);

  const fetchData = async () => {
    try {
      const response = await apiCall(`/purposes/get-purpose/${purposeId}`);
      if (response) {
        setFormData({
          purpose_category: response?.purpose_category || "",
          purpose_sub_category: response?.purpose_sub_category || "",
          purpose_title: response.purpose_title || "",
          purpose_description: response.purpose_description || "",
          purpose_priority: response.purpose_priority || "high",
          review_frequency: response.review_frequency || "quarterly",
          data_elements: response.data_elements || [],
          service_mandatory: response.service_mandatory || false,
          service_mandatory_de: response.service_mandatory_de || [],
          service_message: response.service_message || "",
          legal_mandatory: response.legal_mandatory || false,
          legal_message: response.legal_message || "",
          consent_time_period: response.consent_time_period || 0,
          translations: response.translations || {},
          reconsent: response.reconsent || false,
        });
      }
      setOriginalData(response);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const validateMissingFields = () => {
    const missing = [];
    let missingTranslation = [];

    const checks = [
      { value: formData.purpose_title, label: "purpose_title", step: 1 },
      { value: formData.purpose_priority, label: "purpose_priority", step: 1 },
      { value: formData.review_frequency, label: "review_frequency", step: 1 },
      {
        value: formData.consent_time_period,
        label: "consent_time_period",
        step: 1,
      },
    ];

    if (formData.service_mandatory) {
      checks.push(
        {
          value: formData.service_mandatory_de?.length,
          label: "service_mandatory_de",
          step: 2,
        },
        { value: formData.service_message, label: "service_message", step: 2 }
      );
    }

    if (formData.legal_mandatory) {
      checks.push({
        value: formData.legal_message,
        label: "legal_message",
        step: 2,
      });
    }

    if (activeStep === 3) {
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

      allLanguages.forEach((langCode) => {
        const value = formData.translations?.[langCode];
        if (!value || (typeof value === "string" && !value.trim())) {
          const langLabel = getLanguageLabel(langCode);
          missingTranslation.push(langLabel);
        }
      });

      if (missingTranslation.length > 0) {
        setShowModal(missingTranslation);
      }
    }

    checks.forEach(({ value, label, step }) => {
      if (step === activeStep) {
        const isEmpty =
          typeof value === "string" ? !value.trim() : value === 0 || !value;
        if (isEmpty) missing.push(label);
      }
    });

    return { missing, missingTranslation };
  };

  const handleSubmit = async (status, isDraftClick = false) => {
    try {
      setLoading(true);

      const data = {
        purpose_category: formData.purpose_category,
        purpose_sub_category: formData.purpose_sub_category,
        purpose_title: formData.purpose_title,
        purpose_description: formData.purpose_description,
        purpose_priority: formData.purpose_priority,
        review_frequency: formData.review_frequency,
        consent_time_period: formData.consent_time_period || 0,
        reconsent: formData.reconsent || false,
        data_elements:
          formData.data_elements?.map((el) => ({
            de_id: el.de_id,
            de_name: el.de_name,
            service_mandatory: el.service_mandatory || false,
            service_message: el.service_message || "",
            legal_mandatory: el.legal_mandatory || false,
            legal_message: el.legal_message || "",
          })) || [],
        translations: { ...formData.translations },
      };

      if (!isDraftClick) {
        const { missing, missingTranslation } = validateMissingFields();

        if (missing.length > 0 || missingTranslation.length > 0) {
          setMissingFields(missing);
          toast.error(
            `Please fill all the required fields. ${missing.join(", ")}`
          );
          return;
        }
      }

      let createdId = purposeId;
      if (activeStep == 3 || isDraftClick) {
        if (isValidObjectId(purposeId)) {
          if (data?.translations?.eng) {
            delete data?.translations?.eng;
          }

          let updatedData = getUpdatedFields(originalData, data);
          if (Object.keys(updatedData).length > 0) {
            const res = await apiCall(`/purposes/update-purpose/${purposeId}`, {
              method: "PUT",
              data: updatedData,
            });
            createdId = res?.purpose_id || purposeId;
            if (status !== "published") {
              toast.success("Purpose Updated Successfully");
            }
            setOriginalData({ ...originalData, ...updatedData });
          }
        } else {
          const res = await apiCall(`/purposes/create-purpose`, {
            method: "POST",
            data,
          });
          createdId = res?.purpose_id;
          if (status !== "published") {
            toast.success(
              isDraftClick ? "Saved as Draft" : "Created Successfully"
            );
          }
        }
      } else {
        setActiveStep(parseInt(activeStep) + 1);
        return;
      }

      if (!createdId) throw new Error("Purpose ID not found from API response");

      if (status === "published") {
        await apiCall(`/purposes/publish-purpose/${createdId}`, {
          method: "PATCH",
        });
        toast.success("Purpose Published Successfully");
        router.push(`/apps/purpose-management`);
      } else if (isDraftClick) {
        router.push(`/apps/purpose-management`);
      } else {
        handleTabChange(activeStep + 1);
      }
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex h-full flex-col justify-between">
      <div className="w-full">
        <Header title="Create Purpose" breadcrumbsProps={breadcrumbsProps} />
      </div>

      <Stepper
        steps={["Step 1", "Step 2", "Step 3"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
      />

      <div className="custom-scrollbar flex h-[calc(100vh-210px)] w-full justify-center overflow-auto">
        <div className="flex h-auto w-full justify-center">
          {activeStep == 1 && (
            <CreateStep1
              formData={formData}
              updateField={updateField}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}

          {activeStep == 2 && (
            <CreateStep2
              formData={formData}
              updateField={updateField}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
          {activeStep == 3 && (
            <CreateStep3
              formData={formData}
              updateField={updateField}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
        </div>
        {showModal && (
          <MissingTranslationsModal
            missing={showModal}
            onClose={() => setShowModal(false)}
            onSaveDraft={() => handleSubmit("draft", true)}
          />
        )}
        <StickyFooterActions
          showCancel={activeStep === 1}
          onCancelHref="/apps/purpose-management"
          showBack={activeStep > 1}
          onBack={handlePrevStep}
          showPublish={true}
          onPublish={() => {
            handleSubmit(activeStep == 3 ? "published" : "draft", false);
          }}
          onSaveAsDraft={() => handleSubmit("draft", true)}
          showSaveAsDraft={true}
          publishLabel={
            activeStep === 3 ? (
              "Publish"
            ) : (
              <>
                Next <FaArrowRight />
              </>
            )
          }
          className="mt-10 py-4 shadow-xl"
        />
      </div>
    </div>
  );
};

export default Page;
