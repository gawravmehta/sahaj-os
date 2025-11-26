"use client";

import StepOne from "@/components/features/dpar/step/StepOne";
import StepThree from "@/components/features/dpar/step/StepThree";
import StepTwo from "@/components/features/dpar/step/StepTwo";
import Header from "@/components/ui/Header";
import Stepper from "@/components/ui/Stepper";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { apiCall, uploadFile } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";
import { FaArrowRight } from "react-icons/fa";

const AddNewRequest = () => {
  const router = useRouter();

  const [activeStep, setActiveStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [country, setCountry] = useState([]);
  const [category, setCategory] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [coreIdentifier, setCoreIdentifier] = useState("");
  const [secondaryIdentifier, setSecondaryIdentifier] = useState(null);

  const [priority, setPriority] = useState([]);
  const [type, setType] = useState([]);
  const [relatedRequest, setRelatedRequest] = useState("");
  const [relatedType, setRelatedType] = useState([]);

  const [visible, setVisible] = useState(false);
  const [active, setActive] = useState(false);
  const [selectedKycType, setSelectedKycType] = useState(null);
  const [fileFront, setFileFront] = useState(null);
  const [fileBack, setFileBack] = useState(null);
  const [attachmentFiles, setAttachmentFiles] = useState([]);

  const breadcrumbsProps = {
    path: "/apps/dpar/create-request",
    skip: "/apps",
  };

  const handleNextStep = () => {
    if (!firstName.trim()) {
      toast.error("Please enter a First Name before proceeding.");
      return;
    }
    if (activeStep < 3) {
      setActiveStep(activeStep + 1);
    }
  };

  const handlePrevStep = () => {
    if (activeStep > 1) {
      setActiveStep(activeStep - 1);
    }
  };

  const handleStepClick = (step) => {
    setActiveStep(step);
  };

  const uploadAllFiles = async (dparRequestId) => {
    const formData = new FormData();
    let hasFiles = false;

    if (
      selectedKycType &&
      selectedKycType !== "Request KYC" &&
      selectedKycType !== "Not Required"
    ) {
      if (fileFront) {
        formData.append("kyc_front", fileFront);
        hasFiles = true;
      }
      if (fileBack) {
        formData.append("kyc_back", fileBack);
        hasFiles = true;
      }
    }

    if (attachmentFiles.length > 0) {
      attachmentFiles.forEach((file) => {
        formData.append("upload_attachments", file);
      });
      hasFiles = true;
    }

    if (!hasFiles) return;

    try {
      const endpoint = `/dpar/upload-kyc-document?request_id=${dparRequestId}`;
      await uploadFile(endpoint, formData);
      toast.success("Files uploaded successfully!");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    try {
      const getValue = (value) =>
        typeof value === "object" ? value.value : value;

      const payload = {
        first_name: firstName,
        last_name: lastName,
        core_identifier: coreIdentifier,
        secondary_identifier: secondaryIdentifier,
        dp_type: getValue(category),
        country: getValue(country),
        request_priority: getValue(priority),
        request_type: getValue(type),
        request_message: "This is a default message for the request.",
        kyc_document:
          selectedKycType === "Not Required" ? null : selectedKycType,
        related_request: relatedRequest,
        related_request_type: getValue(relatedType),
      };

      const response = await apiCall("/dpar/make-request", {
        method: "POST",
        data: payload,
      });

      const dparRequestId = response?.dpar_request_id;
      if (!dparRequestId) throw new Error("No request ID returned from API");

      toast.success("Request created successfully!");

      await uploadAllFiles(dparRequestId);

      router.push("/apps/dpar");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header
        title="Create Incoming Request"
        breadcrumbsProps={breadcrumbsProps}
      />

      <Stepper
        steps={["Step 1", "Step 2", "Step 3"]}
        activeStep={activeStep}
        onStepClick={handleStepClick}
      />

      <div className="flex items-center justify-center">
        <div className="custom-scrollbar flex h-[calc(100vh-240px)] w-full justify-center overflow-y-auto pt-6">
          <div className="w-[480px]">
            {activeStep === 1 && (
              <StepOne
                country={country}
                setCountry={setCountry}
                category={category}
                setCategory={setCategory}
                firstName={firstName}
                setFirstName={setFirstName}
                lastName={lastName}
                setLastName={setLastName}
                coreIdentifier={coreIdentifier}
                setCoreIdentifier={setCoreIdentifier}
                secondaryIdentifier={secondaryIdentifier}
                setSecondaryIdentifier={setSecondaryIdentifier}
              />
            )}
            {activeStep === 2 && (
              <StepTwo
                type={type}
                priority={priority}
                setPriority={setPriority}
                setType={setType}
                relatedRequest={relatedRequest}
                setRelatedRequest={setRelatedRequest}
                relatedType={relatedType}
                setRelatedType={setRelatedType}
              />
            )}
            {activeStep === 3 && (
              <StepThree
                visible={visible}
                setVisible={setVisible}
                active={active}
                setActive={setActive}
                selectedKycType={selectedKycType}
                setSelectedKycType={setSelectedKycType}
                setFileFront={setFileFront}
                fileFront={fileFront}
                setFileBack={setFileBack}
                fileBack={fileBack}
                attachmentFiles={attachmentFiles}
                setAttachmentFiles={setAttachmentFiles}
              />
            )}
          </div>
        </div>

        <StickyFooterActions
          onCancelHref="/user/dpar"
          showCancel={activeStep === 1}
          showBack={activeStep > 1}
          onBack={handlePrevStep}
          showSubmit
          onSubmit={activeStep === 3 ? handleSubmit : handleNextStep}
          submitLabel={activeStep === 3 ? "Submit" : "Next"}
          btnLoading={isSubmitting}
          isNextDisabled={activeStep < 3 && !firstName.trim()}
        >
          {() =>
            activeStep < 3 ? <FaArrowRight className="text-[12px]" /> : null
          }
        </StickyFooterActions>
      </div>
    </>
  );
};

export default AddNewRequest;
