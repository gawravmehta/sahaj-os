"use client";
import Header from "@/components/ui/Header";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { useRouter, useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import Stepper from "@/components/ui/Stepper";
import CreateStep2 from "@/components/features/cookieManagement/CreateStep2";
import CreateStep1 from "@/components/features/cookieManagement/CreateStep1";
import { getLanguageLabel } from "@/utils/helperFunctions";
import MissingTranslationsModal from "@/components/shared/modals/MissingTranslationsModal";

const Page = () => {
  const params = useParams();
  const website_id = params?.website_id;
  const router = useRouter();
  const searchParams = useSearchParams();

  const cookieId = searchParams.get("id");
  const pageType = searchParams.get("type") || "create";

  const [formData, setFormData] = useState({
    cookie_name: "",
    description: "",
    hostname: "",
    category: "",
    lifespan: "",
    path: "/",
    http_only: false,
    secure: false,
    same_site: "Lax",
    is_third_party: false,
    cookie_status: "draft",
  });

  const [btnLoading, setBtnLoading] = useState(false);
  const [originalData, setOriginalData] = useState(null);
  const [missingFields, setMissingFields] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);
  const [activeStep, setActiveStep] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [missingTranslation, setMissingTranslation] = useState([]);

  useEffect(() => {
    if (pageType === "edit" && cookieId) {
      getCookie();
    }
  }, [cookieId, pageType]);

  const getCookie = async () => {
    try {
      const response = await apiCall(`/cookie/get-cookie/${cookieId}`);
      setFormData(response);
      setOriginalData(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

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

  const handleSave = async (published) => {
    try {
      setBtnLoading(true);
      if (published) {
        let missing = [];

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
          setBtnLoading(false);
          return;
        }
      }

      if (pageType === "edit" && cookieId) {
        let updatedFields = getUpdatedFields(originalData, {
          ...formData,
          cookie_status: published ? "published" : "draft",
        });

        if (Object.keys(updatedFields).length === 0) {
          toast("No changes detected.");
          router.push(`/apps/cookie-management/${website_id}`);
          return;
        }

        await apiCall(`/cookie/update-cookie/${cookieId}`, {
          method: "PUT",
          data: updatedFields,
        });
      } else {
        await apiCall(`/cookie/create-cookie?website_id=${website_id}`, {
          method: "POST",
          data: {
            ...formData,
            cookie_status: published ? "published" : "draft",
          },
        });
      }

      if (published) {
        toast.success("Cookie published successfully");
      } else {
        toast.success("Cookie saved as draft");
      }

      router.push(`/apps/cookie-management/${website_id}`);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setBtnLoading(false);
    }
  };

  const updateField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="flex h-full flex-col justify-between">
      <Header
        title={pageType === "edit" ? `Edit Cookie` : "Add Cookie"}
        subtitle={
          pageType === "edit"
            ? "Update cookie details for this website"
            : "Add cookie details for this website"
        }
      />

      <Stepper
        steps={["General Info", "Additional Settings"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
        className="max-w-xl"
      />

      <div className="flex h-[calc(100vh-233px)] w-full justify-center overflow-auto custom-scrollbar pb-5">
        {activeStep === 1 && (
          <CreateStep1
            formData={formData}
            setFormData={setFormData}
            missingFields={missingFields}
            wrongFields={wrongFields}
          />
        )}
        {activeStep === 2 && (
          <CreateStep2
            formData={formData}
            setFormData={setFormData}
            updateField={updateField}
          />
        )}

        {showModal && (
          <MissingTranslationsModal
            missing={missingTranslation}
            onClose={() => setShowModal(false)}
            module="Cookie"
            onSaveDraft={() => handleSaveOrPublish("draft")}
          />
        )}
      </div>

      <StickyFooterActions
        btnLoading={btnLoading}
        showCancel={activeStep === 1}
        onCancelHref={`/apps/cookie-management/${website_id}`}
        showBack={activeStep === 2}
        onBack={() => setActiveStep(1)}
        showSubmit
        onSubmit={
          activeStep === 1 ? () => setActiveStep(2) : () => handleSave(true)
        }
        submitLabel={activeStep === 1 ? "Next" : "Publish"}
        showSaveAsDraft
        onSaveAsDraft={() => handleSave(false)}
        className="mt-10 py-4 shadow-xl"
      />
    </div>
  );
};

export default Page;
