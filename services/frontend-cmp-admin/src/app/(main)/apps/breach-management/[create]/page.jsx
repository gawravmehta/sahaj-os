"use client";
import ComplianceStep3 from "@/components/features/breachManagement/ComplianceStep3";
import GeneralInfoStep1 from "@/components/features/breachManagement/GeneralInfoStep1";
import RegulatoryInfoStep2 from "@/components/features/breachManagement/RegulatoryInfoStep2";
import WorkflowStages from "@/components/features/breachManagement/WorkflowStages";
import Header from "@/components/ui/Header";
import Stepper from "@/components/ui/Stepper";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { useRouter, useSearchParams } from "next/navigation";
import React, { use, useCallback, useState } from "react";
import { FaArrowRight } from "react-icons/fa6";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";

const Page = ({ params }) => {
  const { create: elementId } = use(params);
  const [searchParams] = useSearchParams();
  const router = useRouter();

  const [missingFields, setMissingFields] = useState([]);
  const [originalData, setOriginalData] = useState(null);

  const handleTabChange = (tabId) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("activeTab", tabId);
    router.push(`?${params.toString()}`, { shallow: true });
  };

  const isCreate = elementId === "create";

  const getOneBreachIncident = async () => {
    try {
      const response = await apiCall(`/incidents/get-incidents/${elementId}`);
      setFormData(response || {});
      setOriginalData(response || {});
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  React.useEffect(() => {
    if (!isCreate) {
      getOneBreachIncident();
    }
  }, [isCreate, elementId]);

  const validateStep1 = () => {
    const required = ["incident_name", "incident_type", "incident_sensitivity"];
    const missing = required.filter(
      (f) =>
        !formData[f] || (typeof formData[f] === "string" && !formData[f].trim())
    );
    setMissingFields(missing);
    return missing.length === 0;
  };

  const handleSaveOrPublish = async (action) => {
    if (!validateStep1()) {
      toast.error("Please fill in all required fields in Step 1");
      return;
    }

    try {
      const payload = { ...formData };

      const dateFields = [
        "date_occurred",
        "date_discovered",
        "deadline",
        "date_closed",
        "created_at",
        "regulatory_reported_date",
        "notification_sent_date",
      ];

      dateFields.forEach((field) => {
        if (payload[field] === "") {
          payload[field] = null;
        }
      });

      if (action === "draft") {
        payload.status = "draft";
      }

      let url = "/incidents/create-or-update";
      if (!isCreate) {
        url += `?incident_id=${elementId}`;
      }

      const response = await apiCall(url, {
        method: "POST",
        data: payload,
      });

      const savedId =
        response?.incident_id || response?._id || (isCreate ? null : elementId);

      if (!savedId) {
        if (!isCreate) {
        } else {
          throw new Error("Failed to retrieve Incident ID after save.");
        }
      }

      if (action === "publish") {
        await apiCall(`/incidents/${savedId}/publish`, {
          method: "POST",
        });
        toast.success("Breach Incident Published Successfully");
      } else {
        toast.success("Breach Incident Saved as Draft");
      }

      router.push("/apps/breach-management");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleNextStep = () => {
    if (activeStep === 1 && !validateStep1()) {
      toast.error("Please fill in all required fields");
      return;
    }
    setActiveStep((prev) => prev + 1);
    handleTabChange(activeStep + 1);
  };

  const handleDataChange = useCallback((field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const handlePrevStep = () => {
    if (activeStep > 1) {
      setActiveStep(activeStep - 1);
      handleTabChange(activeStep - 1);
    }
  };

  const [formData, setFormData] = useState({
    incident_name: "",
    incident_type: "",
    incident_sensitivity: "",
    description: "",
    status: "draft",
    current_stage: "",
    assignee: "",
    workflow: [],
    template_used: "",
    date_occurred: "",
    date_discovered: "",
    deadline: "",
    date_closed: "",
    created_at: "",
    data_element: [],
    regulatory_reported: true,
    regulatory_reported_date: "",
    regulatory_authority: "",
    compliance_standard: "",
    notification_needed: true,
    notification_sent: true,
    notification_sent_date: "",
    affected_population: 0,
    mitigation_steps: [""],
  });

  const breadcrumbsProps = {
    path: "/apps/breach-management/create",
    skip: "/apps/",
  };
  const [activeStep, setActiveStep] = useState(
    parseInt(searchParams?.get("activeTab")) || 1
  );
  return (
    <div className="relative flex h-full flex-col justify-between">
      <div className="w-full">
        <Header title="Create Breach" breadcrumbsProps={breadcrumbsProps} />
      </div>

      <Stepper
        steps={["Step 1", "Step 2", "Step 3", "Step 4"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
      />
      <div
        className={`custom-scrollbar flex h-[calc(100vh-210px)] w-full justify-center overflow-auto`}
      >
        <div className="flex h-auto w-full justify-center">
          {activeStep == 1 && (
            <GeneralInfoStep1
              formData={formData}
              setFormData={setFormData}
              handleInputChange={handleDataChange}
              missingFields={missingFields}
            />
          )}
          {activeStep == 2 && (
            <WorkflowStages
              formData={formData}
              setFormData={setFormData}
              handleInputChange={handleDataChange}
              missingFields={missingFields}
            />
          )}

          {activeStep == 3 && (
            <RegulatoryInfoStep2
              formData={formData}
              setFormData={setFormData}
              handleInputChange={handleDataChange}
              missingFields={missingFields}
            />
          )}
          {activeStep == 4 && (
            <ComplianceStep3
              formData={formData}
              setFormData={setFormData}
              handleInputChange={handleDataChange}
              missingFields={missingFields}
            />
          )}
        </div>

        <StickyFooterActions
          showCancel={activeStep === 1}
          onCancelHref="/apps/breach-management"
          showBack={activeStep > 1}
          onBack={handlePrevStep}
          showPublish={true}
          onPublish={() => {
            if (activeStep === 4) {
              handleSaveOrPublish("publish");
            } else {
              handleNextStep();
            }
          }}
          onSaveAsDraft={() => {
            handleSaveOrPublish("draft");
          }}
          showSaveAsDraft={true}
          publishLabel={
            activeStep !== 4 ? (
              <>
                Next <FaArrowRight />
              </>
            ) : (
              "Publish"
            )
          }
          className="mt-10 py-4 shadow-xl"
        >
          {activeStep !== 4 && <FaArrowRight className="text-[12px]" />}
        </StickyFooterActions>
      </div>
    </div>
  );
};

export default Page;
