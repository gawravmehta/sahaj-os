"use client";

import React, { useEffect, useMemo, useState } from "react";
import { RxCross2 } from "react-icons/rx";
import { IoCheckmark } from "react-icons/io5";
import { MdOutlineTimer } from "react-icons/md";
import { VscDebugRestart } from "react-icons/vsc";
import Button from "@/components/ui/Button";

import New from "./status-steps/New";
import Kyc from "./status-steps/Kyc";
import Review from "./status-steps/Review";
import Compiling from "./status-steps/Compiling";
import DataManipulation from "./status-steps/DataManipulation";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Modal from "@/components/ui/Modal";
import {
  DatePickerField,
  InputField,
  SelectInput,
  TextareaField,
} from "@/components/ui/Inputs";
import Completed from "./status-steps/Completed";

const steps = [
  {
    id: 1,
    uiTitle: "New",
    backendMatch: ["new", "received", "acknowledged"],
    description: "The individual has submitted a request.",
    Component: New,
  },
  {
    id: 2,
    uiTitle: "KYC",
    backendMatch: ["kyc", "kyc_required", "kyc_in_progress", "kyc_failed"],
    description: "Please verify your identity to continue.",
    Component: Kyc,
  },
  {
    id: 3,
    uiTitle: "Review",
    backendMatch: ["review", "triage", "legal_review", "risk_review"],
    description: "We’re reviewing your request internally.",
    Component: Review,
  },
  {
    id: 4,
    uiTitle: "Related Requests",
    backendMatch: [
      "related_req",
      "data_collection",
      "data_preparation",
      "pending_processor",
    ],
    description: "Check if there are any related requests.",
    Component: Compiling,
  },
  {
    id: 5,
    uiTitle: "Download/Update/Delete",
    backendMatch: [
      "approved",
      "update",
      "delete",
      "ready_download",
      "ready_portability",
    ],
    description: "Request available for individual actions.",
    Component: DataManipulation,
  },
  {
    id: 6,
    uiTitle: "Completed",
    backendMatch: ["completed"],
    description: "Completed",
    Component: Completed,
  },
];

const Status = ({ data, onStepChange, onCancelRequest }) => {
  const [clarificationAskModal, setClarificationAskModal] = useState(false);
  const [rejectRequestModal, setRejectRequestModal] = useState(false);

  const [rejectionReason, setRejectionReason] = useState("");

  const clarificationTypeOptions = [
    { value: "incomplete_information", label: "Incomplete Information" },
    { value: "incorrect_information", label: "Incorrect Information" },
    { value: "duplicate_request", label: "Duplicate Request" },
    { value: "additional_documents", label: "Additional Documents" },
    { value: "other", label: "Other" },
  ];

  const actionOptions = [
    { value: "upload_documents", label: "Upload Documents" },
    { value: "update_information", label: "Update Information" },
    { value: "confirm_identity", label: "Confirm Identity" },
  ];

  const [clarificationForm, setClarificationForm] = useState({
    clarification_type: "",
    title: "",
    message: "",
    deadline: "",
    action: "",
  });

  const initialStatus = (data?.status || "new").toLowerCase();

  const initialIndex = useMemo(() => {
    const idx = steps.findIndex((s) => s.backendMatch.includes(initialStatus));
    return idx === -1 ? 0 : idx;
  }, [initialStatus]);

  const [activeIndex, setActiveIndex] = useState(initialIndex);

  useEffect(() => {
    setActiveIndex(initialIndex);
  }, [initialIndex]);

  const isFirst = activeIndex === 0;
  const isLast = activeIndex === steps.length - 1;

  const updatedSteps = steps.map((step, index) => ({
    ...step,
    isCompleted: index <= activeIndex,
  }));

  const goNext = async () => {
    if (isLast) return;

    const currentStatus = steps[activeIndex].backendMatch[0];

    try {
      const response = await apiCall(`/dpar/set/${currentStatus}/${data._id}`, {
        method: "PATCH",
      });

      const nextIndex = activeIndex + 1;
      setActiveIndex(nextIndex);

      onStepChange?.(steps[nextIndex].backendMatch[0], nextIndex);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const goPrev = () => {
    if (isFirst) return;
    const prevIndex = activeIndex - 1;
    setActiveIndex(prevIndex);
    onStepChange?.(steps[prevIndex].backendMatch[0], prevIndex);
  };

  const handleRequestRejection = async () => {
    try {
      const response = await apiCall(`/dpar/set/rejected/${data._id}`, {
        method: "PATCH",
        params: {
          status_details: rejectionReason,
        },
      });

      toast.success(response?.data.message);
      setRejectRequestModal(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleRequestResendingKYC = async () => {
    try {
      const response = await apiCall(
        `/dpar/request/kyc-verifications/${data._id}`,
        {
          method: "PUT",
        }
      );
      toast.success(response?.message.message);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleRequestClarification = async () => {
    const payload = {
      clarification_type: clarificationForm.clarification_type?.value,
      title: clarificationForm.title,
      message: clarificationForm.message,
      deadline: new Date(clarificationForm.deadline).toISOString(),
      action: clarificationForm.action?.value,
    };

    try {
      const response = await apiCall(
        `/dpar/request/clarification/${data?._id}`,
        {
          method: "PUT",
          data: payload,
        }
      );
      toast.success(response?.message.message);
      setClarificationAskModal(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const ActiveComponent = steps[activeIndex].Component;

  return (
    <div className="h-[calc(100vh-175px)] w-full">
      {steps[activeIndex].id !== 6 && (
        <div className="flex justify-end gap-2 border-b border-borderheader px-6 py-2">
          <Button
            variant="cancel"
            className="flex w-40 gap-1"
            onClick={() => setRejectRequestModal(true)}
          >
            <RxCross2 />
            Reject Request
          </Button>
        </div>
      )}

      <div className="flex flex-col px-6 sm:flex sm:flex-row">
        <div className="h-[calc(100vh-230px)] w-full border-r border-borderheader px-1 py-2 lg:w-[30%]">
          {updatedSteps.map((step, index) => (
            <div key={step.id}>
              <div className="flex items-center gap-5">
                <div
                  className={`flex min-h-8 min-w-8 items-center justify-center rounded-full text-white ${
                    step.isCompleted
                      ? "bg-primary"
                      : "border border-[#A1AEBE] text-[#242E39]"
                  }`}
                >
                  {step.isCompleted ? (
                    <IoCheckmark size={15} />
                  ) : (
                    <span className="text-black">{index + 1}</span>
                  )}
                </div>
                <div className="mt-2">
                  <h1
                    className={`font-lato text-[16px] ${
                      index === activeIndex
                        ? "text-primary"
                        : step.isCompleted
                        ? "text-primary/90"
                        : "text-[#242E39]"
                    }`}
                  >
                    {step.uiTitle}
                  </h1>
                  <p className="text-sm font-medium text-[#595959]">
                    {step.description}
                  </p>
                </div>
              </div>

              {index < updatedSteps.length - 1 && (
                <div
                  className={`ml-4 h-6 w-0 outline-dashed outline-[1.3px] ${
                    index < activeIndex
                      ? "outline-primary"
                      : "outline-[#6B7280]"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="flex-1 p-4">
          <div className="mb-4">
            <ActiveComponent data={data} />
          </div>

          <div className="flex items-center justify-between gap-3">
            <div className="mt-3 flex items-center gap-4 text-sm text-[#4B5563]">
              <span className="inline-flex items-center gap-1">
                <MdOutlineTimer /> Step {activeIndex + 1} of {steps.length}
              </span>
              {!isLast ? (
                <span className="inline-flex items-center gap-1">
                  <VscDebugRestart /> Next: {steps[activeIndex + 1].uiTitle}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <IoCheckmark /> Completed
                </span>
              )}
            </div>
            <div className="flex gap-2 items-center">
              {steps[activeIndex].id === 2 && (
                <Button
                  variant="secondary"
                  className="w-32"
                  onClick={handleRequestResendingKYC}
                  title={"Request Resend KYC"}
                >
                  Requst Resend
                </Button>
              )}
              {steps[activeIndex].id === 3 && (
                <Button
                  variant="secondary"
                  className="w-44"
                  onClick={() => setClarificationAskModal(true)}
                  title={"Request Clarification"}
                >
                  Requst Clarification
                </Button>
              )}
              {!isLast && (
                <Button
                  variant="primary"
                  className="w-32"
                  onClick={goNext}
                  title={
                    isLast
                      ? "Already completed"
                      : "Approve and move to next step"
                  }
                >
                  Approve
                </Button>
              )}
            </div>
          </div>

        </div>
        <Modal
          isOpen={clarificationAskModal}
          onClose={() => setClarificationAskModal(false)}
          title="Request Clarification"
        >
          <div className="flex flex-col gap-2">
            <SelectInput
              name="clarification_type"
              label="Clarification Type"
              options={clarificationTypeOptions}
              value={clarificationForm.clarification_type}
              onChange={(type) =>
                setClarificationForm({
                  ...clarificationForm,
                  clarification_type: type,
                })
              }
              placeholder="Select Clarification Type"
              required
              tooltipText="If there is any problem or any clarification is needed then you can request for clarification."
            />
            <InputField
              name="title"
              label="Title"
              placeholder="Enter Title for Clarification"
              value={clarificationForm.title}
              onChange={(e) =>
                setClarificationForm({
                  ...clarificationForm,
                  title: e.target.value,
                })
              }
              required
              tooltipText="Provide the title for the clarification."
            />
            <TextareaField
              label="Message"
              placeholder="Enter Clarification Message"
              value={clarificationForm.message}
              onChange={(e) =>
                setClarificationForm({
                  ...clarificationForm,
                  message: e.target.value,
                })
              }
            />
            <SelectInput
              name="action"
              label="Action Type"
              options={actionOptions}
              value={clarificationForm.action}
              onChange={(action) =>
                setClarificationForm({
                  ...clarificationForm,
                  action: action,
                })
              }
              placeholder="Select Action Type"
              required
              tooltipText="Select the action type for the clarification."
            />
            <DatePickerField
              name="deadline"
              label="Deadline"
              placeholder="Select Deadline"
              selected={clarificationForm.deadline}
              onChange={(date) =>
                setClarificationForm({ ...clarificationForm, deadline: date })
              }
              required
            />
            <div className="flex items-center justify-between pt-2">
              <Button
                variant="secondary"
                className="w-32"
                onClick={() => setClarificationAskModal(false)}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                className="w-32"
                onClick={handleRequestClarification}
              >
                Submit
              </Button>
            </div>
          </div>
        </Modal>

        <Modal
          isOpen={rejectRequestModal}
          onClose={() => setRejectRequestModal(false)}
          title="Request Rejection"
        >
          <TextareaField
            label="Reason for Rejection"
            placeholder="Enter Reason"
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
          />
          <div className="flex items-center justify-between pt-2">
            <Button
              variant="secondary"
              className="w-32"
              onClick={() => setRejectRequestModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              className="w-32"
              onClick={handleRequestRejection}
            >
              Submit
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default Status;
