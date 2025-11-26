"use client";

import Stepper from "@/components/ui/Stepper";
import Header from "@/components/ui/Header";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { apiCall } from "@/hooks/apiCall";
import { useRouter, useSearchParams } from "next/navigation";
import { use, useEffect, useState } from "react";
import { FaArrowRight } from "react-icons/fa";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import ChoosePlatform from "@/components/features/collectionPoint/ChoosePlatform";
import CPStep1 from "@/components/features/collectionPoint/CPStep1";
import CPStep2 from "@/components/features/collectionPoint/CPStep2";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import CpTypeCard from "@/components/features/collectionPoint/CpTypeCard";

const Page = ({ params }) => {
  const { cp_id: cpId } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const [missingFields, setMissingFields] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);

  const [formData, setFormData] = useState({
    cp_name: "",
    cp_description: "",
    cp_type: "",
    redirection_url: "",
    fallback_url: "",
    default_language: "English",
    asset_id: "",
    data_elements: [],
    currentDataElement: [],
    notice_type: "",
    is_verification_required: false,
    notice_popup_window_timeout: 10,
    verification_done_by: "",
    prefered_verification_medium: "",
  });

  const [originalData, setOriginalData] = useState(null);
  const [activeStep, setActiveStep] = useState(
    parseInt(searchParams.get("activeTab")) || 1
  );
  const [btnLoading, setBtnLoading] = useState(false);

  const pageType = searchParams.get("type") || "";

  const handleTabChange = (tabId) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("activeTab", tabId);
    router.push(`?${params.toString()}`, { shallow: true });
  };

  useEffect(() => {
    if (cpId && cpId !== "create-collection-point") {
      getCollectionPoint();
    }
  }, []);

  const getCollectionPoint = async () => {
    try {
      const response = await apiCall(`/cp/get-cp/${cpId}`);
      setFormData({
        cp_name: response.cp_name || "",
        cp_description: response.cp_description || "",
        notice_type: response.notice_type || "",
        cp_type: response.cp_type || "",
        redirection_url: response.redirection_url || "",
        fallback_url: response.fallback_url || "",
        default_language: response.default_language || "eng",
        asset_id: response.asset_id || "",
        is_verification_required: response.is_verification_required || false,
        verification_done_by: response.verification_done_by || "sahaj",
        prefered_verification_medium:
          response.prefered_verification_medium || "",
        notice_popup_window_timeout: response.notice_popup_window_timeout || 10,
        data_elements: response.data_elements || [],
        currentDataElement:
          response.data_elements?.map((de) => ({
            value: de.de_id,
            label: de.de_name,
          })) || [],
      });
      setOriginalData(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const hasStepChanged = (step) => {
    if (!originalData) return true;
    switch (step) {
      case 1:
        return originalData.asset_id !== formData.asset_id;
      case 2:
        return originalData.cp_type !== formData.cp_type;
      case 3:
        return (
          originalData.cp_name !== formData.cp_name ||
          originalData.cp_description !== formData.cp_description ||
          originalData.redirection_url !== formData.redirection_url ||
          originalData.fallback_url !== formData.fallback_url
        );
      case 4:
        return (
          JSON.stringify(originalData.data_elements) !==
            JSON.stringify(formData.data_elements) ||
          formData.notice_type !== originalData.notice_type ||
          formData.is_verification_required !==
            originalData.is_verification_required ||
          formData.notice_popup_window_timeout !==
            originalData.notice_popup_window_timeout ||
          formData.verification_done_by !== originalData.verification_done_by ||
          formData.prefered_verification_medium !==
            originalData.prefered_verification_medium
        );
      default:
        return false;
    }
  };

  const handleNextStep = async (type) => {
    try {
      const missing = [];
      const wrongFields = [];

      if (activeStep === 1) {
        if (!formData.asset_id) missing.push("cpUsagePlatform");
      }
      if (activeStep === 2) {
        if (!formData.cp_type) missing.push("cp_type");
      }
      if (activeStep === 3) {
        if (!formData.cp_name?.trim()) missing.push("cp_name");

        const urlFields = ["redirection_url", "fallback_url"];
        urlFields.forEach((field) => {
          if (formData[field] && !/^https?:\/\//i.test(formData[field])) {
            wrongFields.push({
              value: field,
              message:
                "Please enter a valid URL starting with http:// or https://",
            });
          }
        });
      }
      if (activeStep === 4) {
        if (!formData.notice_type) missing.push("notice_type");
      }

      if (missing.length > 0) {
        setMissingFields(missing);
        toast.error("Please fill in all required fields.");
        return;
      }

      if (wrongFields.length > 0) {
        setWrongFields(wrongFields);
        toast.error("Please correct the highlighted fields.");
        return;
      }

      if (cpId === "create-collection-point") {
        if (activeStep < 4 && !type) {
          setActiveStep(activeStep + 1);
          handleTabChange(activeStep + 1);
          return;
        }

        setBtnLoading(true);
        const { currentDataElement, ...payload } = formData;

        const response = await apiCall("/cp/create-collection-point", {
          method: "POST",
          data: payload,
        });

        toast.success("Collection Point Drafted successfully");
        router.push(
          `/apps/collection-point/createdNoticeView?cpId=${response?.cp_id}`
        );

        return;
      }

      if (cpId !== "create-collection-point") {
        const stepChanged = hasStepChanged(activeStep);
        if (stepChanged) {
          let updatedFields = getUpdatedFields(originalData, formData);
          const { currentDataElement, ...filteredFields } = updatedFields;
          updatedFields = filteredFields;

          if (Object.keys(updatedFields).length > 0) {
            await apiCall(`/cp/update-cp/${cpId}`, {
              method: "PUT",
              data: updatedFields,
            });
            setOriginalData({ ...originalData, ...updatedFields });
          }
        }

        if (activeStep < 4 && !type) {
          setActiveStep(activeStep + 1);
          handleTabChange(activeStep + 1);
        } else {
          if (type === "draft") {
            toast.success("Save as Draft successfully");
            router.push(
              `/apps/collection-point/createdNoticeView?cpId=${cpId}`
            );
          } else {
            handlePublishCP(cpId);
          }
        }
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setBtnLoading(false);
    }
  };

  const handlePrevStep = () => {
    if (activeStep > 1) {
      setActiveStep(activeStep - 1);
      handleTabChange(activeStep - 1);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/collection-point/${
      pageType === "edit"
        ? originalData?.cp_name || "Unnamed"
        : "create-collection-point"
    }`,
    skip: "/apps",
  };

  return (
    <>
      <Header
        title={
          pageType === "edit"
            ? `Edit ${originalData?.cp_name} CP` || "Edit Collection Point"
            : "Create Collection Point"
        }
        breadcrumbsProps={breadcrumbsProps}
      />

      <Stepper
        steps={["Step 1", "Step 2", "Step 3", "Step 4"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
      />

      <div className="custom-scrollbar mb-16 flex h-[calc(100vh-210px)] w-full justify-center overflow-auto">
        <div className="flex h-auto w-full justify-center pb-10">
          {activeStep === 1 && (
            <ChoosePlatform formData={formData} setFormData={setFormData} />
          )}
          {activeStep === 2 && (
            <CpTypeCard
              formData={formData}
              setFormData={setFormData}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
          {activeStep === 3 && (
            <CPStep1
              formData={formData}
              setFormData={setFormData}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
          {activeStep === 4 && (
            <CPStep2
              formData={formData}
              setFormData={setFormData}
              missingFields={missingFields}
            />
          )}
        </div>

        <StickyFooterActions
          btnLoading={btnLoading}
          showCancel={activeStep === 1}
          onCancelHref="/apps/collection-point"
          showBack={activeStep > 1}
          onBack={handlePrevStep}
          showSubmit
          onSubmit={() => {
            setMissingFields([]);
            setWrongFields([]);
            handleNextStep(activeStep == 4 && "draft");
          }}
          submitLabel={"Next"}
          showSaveAsDraft={activeStep > 1 && true}
          onSaveAsDraft={() => {
            setMissingFields([]);
            setWrongFields([]);
            handleNextStep("draft");
          }}
          className="mt-10 py-4 shadow-xl"
        >
          {<FaArrowRight className="text-[12px]" />}
        </StickyFooterActions>
      </div>
    </>
  );
};

export default Page;
