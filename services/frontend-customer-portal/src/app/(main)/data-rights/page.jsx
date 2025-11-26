"use client";

import FileUpload from "@/components/FileUpload";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import React, { useState, useEffect } from "react";
import { FaTimes } from "react-icons/fa";
import {
  KYC_OPTIONS,
  IDENTITY_BUTTONS,
  PRIORITY_OPTIONS,
  REQUEST_TYPE_OPTIONS,
  COUNTRY_OPTIONS,
  FORM_TEXT,
  RELATED_REQUEST_TYPE,
} from "@/constants/formConstants";
import { apiCall, uploadFile } from "@/hooks/apiCall";
import YesNoToggle from "@/components/ui/YesNoToggle";
import toast from "react-hot-toast";
import Button from "@/components/ui/Button";
import ActiveConsentsModal from "@/components/features/makeRequest/ActiveConsentsModal";

function Page() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const requestId = searchParams.get("id");
  const isEditMode = !!requestId;

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    coreIdentifier: "",
    secondaryIdentifier: "",
    requestDetails: "",
    relatedRequest: false,
    relatedRequestId: "",
  });
  const [dparRequests, setDparRequests] = useState([]);
  const [clickedButtons, setClickedButtons] = useState([]);
  const [country, setCountry] = useState(null);
  const [choosePriority, setChoosePriority] = useState(null);
  const [requestType, setRequestType] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [relatedRequestType, setRelatedRequestType] = useState(null);
  const [relatedRequestId, setRelatedRequestId] = useState(null);
  const [selectType, setSelectType] = useState(false);
  const [fileFront, setFileFront] = useState(null);
  const [fileBack, setFileBack] = useState(null);
  const [attachmentFiles, setAttachmentFiles] = useState([]);
  const [errors, setErrors] = useState({ firstName: "" });
  const [existingFiles, setExistingFiles] = useState({
    kycFront: null,
    kycBack: null,
    attachments: [],
  });

  const [dataElementOptions, setDataElementOptions] = useState([]);
  const [selectedDataElement, setSelectedDataElement] = useState([]);
  const [updatedValue, setUpdatedValue] = useState("");

  const [showActiveConsentsModal, setShowActiveConsentsModal] = useState(false);
  const [activeConsentsData, setActiveConsentsData] = useState([]);

  const getErrorMessage = (error) => {
    return (
      error.response?.data?.message || error.message || "An error occurred"
    );
  };
  const fetchUserData = async () => {
    try {
      const response = await apiCall(`/api/v1/auth/me`);
      setFormData((prevFormData) => ({
        ...prevFormData,
        coreIdentifier: response.user.email,
        secondaryIdentifier: response.user.mobile,
      }));
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const fetchDataElements = async () => {
    try {
      const response = await apiCall(`/api/v1/preferences/data-elements/by-dp`);
      const formattedData = response?.data_elements?.map((item) => ({
        value: item.data_element_id,
        label: item.data_element_title,
      }));

      setDataElementOptions(formattedData);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchUserData();
    fetchDataElements();
  }, []);

  useEffect(() => {
    const fetchDparRequests = async () => {
      try {
        const response = await apiCall("/api/v1/dpar/get-my-requests");

        if (response && Array.isArray(response)) {
          const mappedRequests = response.map((item) => ({
            value: item.dpar_id,
            label: item.request_message,
          }));

          setDparRequests(mappedRequests);
        } else {
          toast.error("Failed to load related requests");
        }
      } catch (err) {
        toast.error("Failed to load related requests");
      }
    };

    fetchDparRequests();
  }, []);

  useEffect(() => {
    if (isEditMode) {
      const fetchRequestData = async () => {
        try {
          const response = await apiCall(
            `/api/v1/dpar/get-one-dpar-request?dpar_request_id=${requestId}`
          );
          const data = response;

          setFormData({
            firstName: data.first_name,
            lastName: data.last_name,
            coreIdentifier: data.core_identifier,
            secondaryIdentifier: data.secondary_identifier,
            requestDetails: data.request_message,
            relatedRequest: data.related_request,
            relatedRequestId: data.related_request_id || "",
          });

          setCountry(COUNTRY_OPTIONS.find((opt) => opt.value === data.country));
          setChoosePriority(
            PRIORITY_OPTIONS.find((opt) => opt.value === data.request_priority)
          );
          setRequestType(
            REQUEST_TYPE_OPTIONS.find((opt) => opt.value === data.request_type)
          );

          if (data.related_request) {
            setRelatedRequestType(
              RELATED_REQUEST_TYPE.find(
                (opt) => opt.value === data.related_request_type
              )
            );

            if (data.related_request_id) {
              const selectedRequest = dparRequests.find(
                (req) => req.value === data.related_request_id
              );
              if (selectedRequest) {
                setRelatedRequestId(selectedRequest);
              }
            }
          }

          if (data.dp_type) {
            setClickedButtons([data.dp_type]);
          }

          if (data.kyc_document) {
            const kycIndex = KYC_OPTIONS.findIndex(
              (opt) => opt.label === data.kyc_document
            );
            if (kycIndex !== -1) {
              setSelectType(kycIndex);
            }
          }

          setExistingFiles({
            kycFront: data.kyc_front_url,
            kycBack: data.kyc_back_url,
            attachments: data.attachments || [],
          });
        } catch (error) {
          toast.error("Failed to fetch request data");
        }
      };
      fetchRequestData();
    }
  }, [isEditMode, requestId, dparRequests]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (name === "firstName" && errors.firstName) {
      setErrors((prev) => ({ ...prev, firstName: "" }));
    }
  };

  const handleSelectChange = (name, value) => {
    if (name === "relatedRequestId") {
      setRelatedRequestId(value);
      setFormData((prev) => ({
        ...prev,
        relatedRequestId: value ? value.value : "",
      }));
    }
  };

  const validateForm = () => {
    const newErrors = { firstName: "" };
    let isValid = true;

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const isFormValid = () => {
    return formData.firstName.trim() !== "";
  };

  const handleSelectType = (index) => {
    setSelectType(index);
  };

  const handleButtonClick = (buttonLabel) => {
    setClickedButtons((prevClicked) =>
      prevClicked.includes(buttonLabel)
        ? prevClicked.filter((label) => label !== buttonLabel)
        : [buttonLabel]
    );
  };

  const handleRemoveFile = (fileType) => {
    switch (fileType) {
      case "front":
        setFileFront(null);
        setExistingFiles((prev) => ({ ...prev, kycFront: null }));
        break;
      case "back":
        setFileBack(null);
        setExistingFiles((prev) => ({ ...prev, kycBack: null }));
        break;
      case "attachment":
        setAttachmentFiles([]);
        setExistingFiles((prev) => ({ ...prev, attachments: [] }));
        break;
      default:
        break;
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsSubmitting(true);

    try {
      const requestData = {
        df_id: process.env.NEXT_PUBLIC_DF_ID,
        first_name: formData.firstName,
        last_name: formData.lastName,
        core_identifier: formData.coreIdentifier,
        secondary_identifier: formData.secondaryIdentifier,
        dp_type: clickedButtons[0] || "person",
        country: country?.value || "",
        request_priority: choosePriority?.value || "",
        request_type: requestType?.value || "",
        data_element_id: selectedDataElement?.value || "",
        data_element_updated_value: updatedValue || "",
        request_message: formData.requestDetails,
        kyc_document:
          selectType !== false ? KYC_OPTIONS[selectType]?.label : "",
        related_request: formData.relatedRequest,
        related_request_type: relatedRequestType?.value || "",
        related_request_id: formData.relatedRequestId,
      };

      let response;
      if (isEditMode) {
        response = await apiCall(`/api/v1/dpar/dpa-requests/${requestId}`, {
          method: "PUT",
          data: requestData,
        });
      } else {
        response = await apiCall("/api/v1/dpar/create-request", {
          method: "POST",
          data: requestData,
        });
      }

      const dparRequestId = isEditMode ? requestId : response?.dpar_request_id;
      if (!dparRequestId) throw new Error("No request ID returned from API");

      toast.success(
        response.message ||
          (isEditMode
            ? "Request updated successfully"
            : "Request created successfully")
      );

      if (
        fileFront ||
        fileBack ||
        (attachmentFiles && attachmentFiles.length > 0)
      ) {
        const uploadFormData = new FormData();
        uploadFormData.append("request_id", dparRequestId);

        if (fileFront) uploadFormData.append("kyc_front", fileFront);
        if (fileBack) uploadFormData.append("kyc_back", fileBack);

        if (attachmentFiles && attachmentFiles.length > 0) {
          Array.from(attachmentFiles).forEach((file) => {
            uploadFormData.append("files", file);
          });
        }

        await uploadFile("/api/v1/kyc/upload-kyc-documents", {
          data: uploadFormData,
        });

        toast.success("Files uploaded successfully!");
      }

      router.push("/past-request");
    } catch (error) {
      if (error?.status === 400) {
        setShowActiveConsentsModal(true);
        setActiveConsentsData(error?.data?.detail?.active_consents);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex justify-center items-center w-full pt-20">
      <div className="w-[622px]">
        <div>
          <h1 className="text-[#000000] text-[28px] font-medium">
            {isEditMode ? "Edit Request" : FORM_TEXT.TITLE}
          </h1>
          <p className="text-subHeading text-sm">{FORM_TEXT.DESCRIPTION}</p>
          <div className="md:w-full md:pr-16 lg:px-0 w-full lg:w-full xl:w-full 2xl:w-full">
            <form
              onSubmit={handleSubmit}
              className="mt-5 w-full flex flex-col gap-y-5 pb-20"
            >
              <h2 className="text-xl lg:2xl">{FORM_TEXT.PERSONAL_INFO}</h2>
              <div className="sm:flex gap-6 w-full">
                <div className="w-1/2">
                  <InputField
                    label="First Name"
                    name="firstName"
                    placeholder="Enter First Name"
                    value={formData.firstName}
                    onChange={handleChange}
                    tooltipText="Enter First Name"
                    required
                    error={errors.firstName}
                    className="bg-transparent"
                  />
                </div>
                <div className="w-1/2">
                  <InputField
                    label="Last Name"
                    name="lastName"
                    placeholder="Enter Last Name"
                    value={formData.lastName}
                    onChange={handleChange}
                    tooltipText="Enter Last Name"
                    className="bg-transparent"
                  />
                </div>
              </div>

              <div className="sm:flex justify-between gap-6 w-full">
                <div className="w-1/2">
                  <InputField
                    label="Core Identifier"
                    name="coreIdentifier"
                    placeholder="Enter Email or Mobile Number"
                    value={formData.coreIdentifier}
                    onChange={handleChange}
                    tooltipText="Enter Email or Mobile Number"
                    className="bg-transparent"
                  />
                </div>
                <div className="w-1/2">
                  <InputField
                    label="Secondary Identifier"
                    name="secondaryIdentifier"
                    placeholder="Enter Email or Mobile Number"
                    value={formData.secondaryIdentifier}
                    onChange={handleChange}
                    tooltipText="Enter Email or Mobile Number"
                    className="bg-transparent"
                  />
                </div>
              </div>

              <div className="w-full h-px bg-[#EEEEEE] my-2"></div>

              <div className="">
                <h2 className="text-xl lg:2xl">{FORM_TEXT.IDENTITY_DETAILS}</h2>
              </div>
              <div className="flex gap-6 w-full">
                <div className="w-full sm:flex sm:flex-col gap-3">
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
                  tooltipText="Select your country"
                  className="bg-transparent"
                />
              </div>

              <div className="w-full h-px bg-[#EEEEEE] my-2"></div>

              <h2 className="text-xl lg:2xl">{FORM_TEXT.REQUEST_INFO}</h2>
              <div className="sm:flex w-full gap-6">
                <div className="w-1/2">
                  <SelectInput
                    label="Request Type"
                    options={REQUEST_TYPE_OPTIONS}
                    value={requestType}
                    onChange={(selected) => setRequestType(selected)}
                    placeholder="Select request"
                    tooltipText="Select request type"
                    className="bg-transparent"
                  />
                </div>
                <div className="w-1/2">
                  <SelectInput
                    label="Request Priority"
                    options={PRIORITY_OPTIONS}
                    value={choosePriority}
                    onChange={(selected) => setChoosePriority(selected)}
                    placeholder="Select Priority"
                    tooltipText="Select request priority"
                    className="bg-transparent"
                  />
                </div>
              </div>
              <div className="sm:flex w-full gap-6">
                {requestType?.value && (
                  <div
                    className={`${
                      requestType?.value === "update_data" ? "w-1/2" : "w-full"
                    }`}
                  >
                    <SelectInput
                      label="Data Element"
                      options={dataElementOptions}
                      value={selectedDataElement}
                      onChange={(selected) => setSelectedDataElement(selected)}
                      placeholder="Select Data Element"
                      tooltipText="Select Required Data Element To be Updated"
                      className="bg-transparent"
                    />
                  </div>
                )}
                {requestType?.value === "update_data" && (
                  <div className="w-1/2">
                    <InputField
                      label="Updated Value"
                      value={updatedValue}
                      onChange={(e) => setUpdatedValue(e.target.value)}
                      placeholder="Updated Value"
                      tooltipText="String of thing that you want to update"
                      className="bg-transparent"
                    />
                  </div>
                )}
              </div>
              <TextareaField
                label="Request Details"
                name="requestDetails"
                placeholder="Write your request"
                value={formData.requestDetails}
                onChange={handleChange}
                tooltipText="Enter request details"
                className="bg-transparent"
              />

              <div className="w-full h-px bg-[#EEEEEE] my-2"></div>

              <div className="">
                <h2 className="text-xl pb-4 lg:2xl">KYC Verification</h2>
                <div className="flex flex-col gap-3">
                  <div className="min-w-max">Select Type</div>
                  <div className="grid sm:grid-cols-3 lg:grid-cols-4 gap-3 w-full">
                    {KYC_OPTIONS.map((kyc, index) => (
                      <div
                        key={index}
                        onClick={() => handleSelectType(index)}
                        className={`flex items-center border gap-x-4 px-2 py-1 cursor-pointer  ${
                          selectType === index
                            ? "border-primary border"
                            : "border-[#C7CFE2] hover:border-hover"
                        }`}
                      >
                        <div className=" w-7 h-7 flex items-center">
                          <Image
                            src={kyc.src}
                            alt={kyc.label}
                            height={100}
                            width={100}
                            className="w-full object-fill"
                          />
                        </div>
                        <div className="text-xs text-[#000000]">
                          {kyc.label}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {(selectType !== false ||
                  existingFiles.kycFront ||
                  existingFiles.kycBack) && (
                  <div className="flex flex-col mt-3">
                    <div className="min-w-max">Upload Images</div>
                    <div className="sm:flex gap-6">
                      <div className="w-1/2">
                        <FileUpload
                          title="Front Side KYC"
                          onFileSelect={setFileFront}
                          existingFile={existingFiles.kycFront}
                          onRemoveFile={() => handleRemoveFile("front")}
                        />
                      </div>
                      <div className="w-1/2">
                        <FileUpload
                          title="Back Side KYC"
                          onFileSelect={setFileBack}
                          existingFile={existingFiles.kycBack}
                          onRemoveFile={() => handleRemoveFile("back")}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="">
                <YesNoToggle
                  label="Is this request related to another request?"
                  value={formData.relatedRequest}
                  onChange={(name, value) => {
                    setFormData((prev) => ({
                      ...prev,
                      relatedRequest: value,
                    }));
                    if (!value) {
                      setRelatedRequestType(null);
                      setRelatedRequestId(null);
                    }
                  }}
                  tooltipText="Select if this is related to another request"
                />
              </div>

              {formData.relatedRequest && (
                <>
                  <SelectInput
                    label="Related Request Type"
                    options={RELATED_REQUEST_TYPE}
                    value={relatedRequestType}
                    onChange={(selected) => setRelatedRequestType(selected)}
                    placeholder="Select request type"
                    className="bg-transparent w-full"
                  />

                  <SelectInput
                    label="Related Request"
                    options={dparRequests}
                    value={relatedRequestId}
                    onChange={(selected) =>
                      handleSelectChange("relatedRequestId", selected)
                    }
                    placeholder="Select related request"
                    className="bg-transparent w-full"
                  />

                  <div className="md:flex flex-col w-full">
                    <h2 className="text-sm text-[#000000]">Upload Documents</h2>
                    <div className="w-full">
                      <FileUpload
                        title="Supporting Documents"
                        existingFiles={existingFiles.attachments}
                        onRemoveFile={() => handleRemoveFile("attachment")}
                        multiple
                        onFileSelect={(files) => setAttachmentFiles(files)}
                      />
                    </div>
                  </div>
                </>
              )}

              <div className="bottom-0 left-0 right-0  py-4 flex justify-end gap-2">
                <Button
                  variant="cancel"
                  type="button"
                  onClick={() => router.push("/past-request")}
                >
                  Cancel
                </Button>
                <Button
                  variant={isFormValid() ? "primary" : "ghost"}
                  type="submit"
                  disabled={!isFormValid() || isSubmitting}
                  className={`min-w-[50px] rounded-none px-3`}
                >
                  {isSubmitting ? (
                    <span className="flex items-center justify-center gap-2">
                      {isEditMode ? "Updating..." : "Submitting..."}
                    </span>
                  ) : isEditMode ? (
                    "Update"
                  ) : (
                    "Submit"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <ActiveConsentsModal
        isOpen={showActiveConsentsModal}
        onClose={() => setShowActiveConsentsModal(false)}
        activeConsents={activeConsentsData}
      />
    </div>
  );
}

export default Page;
