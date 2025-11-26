"use client";

import React, { useState } from "react";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import Button from "@/components/ui/Button";
import FileUpload from "@/components/FileUpload";
import { apiCall, uploadFile } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import {
  SUB_CATEGORY_OPTIONS,
  CATEGORY_OPTIONS,
  DP_IDENTITY,
} from "@/constants/formConstants";
import { FaTimes } from "react-icons/fa";
import { useEffect } from "react";
import Modal from "@/components/features/makeRequest/Modal";

const Page = () => {
  const router = useRouter();

  const [formData, setFormData] = useState({
    email: "",
    mobile_number: "",
    subject: "",
    message: "",
    category: "",
    sub_category: "",
    dp_type: [],
    business_entity: [],
    data_processor: [],
  });

  const [errors, setErrors] = useState({});
  const [attachmentFiles, setAttachmentFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [clickedButtons, setClickedButtons] = useState([]);
  const [availableSubCategories, setAvailableSubCategories] = useState([]);

  const [showModal, setShowModal] = useState(false);
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await apiCall(`/api/v1/auth/me`);

        setFormData((prevFormData) => ({
          ...prevFormData,
          email: response.user.email,
          mobile_number: response.user.mobile,
        }));
      } catch (error) {
        toast.error(getErrorMessage(error));
      }
    };

    fetchUserData();
  }, []);
  useEffect(() => {
    if (formData.category) {
      const subCategories = SUB_CATEGORY_OPTIONS[formData.category] || [];
      setAvailableSubCategories(subCategories);
      setFormData((prev) => ({ ...prev, sub_category: "" }));
    } else {
      setAvailableSubCategories([]);
    }
  }, [formData.category]);

  const handleButtonClick = (buttonLabel) => {
    if (clickedButtons.includes(buttonLabel)) {
      setClickedButtons(clickedButtons.filter((btn) => btn !== buttonLabel));
      setFormData((prev) => ({
        ...prev,
        dp_type: prev.dp_type.filter((item) => item !== buttonLabel),
      }));
    } else {
      setClickedButtons([...clickedButtons, buttonLabel]);
      setFormData((prev) => ({
        ...prev,
        dp_type: [...prev.dp_type, buttonLabel],
      }));
    }

    if (errors.dp_type) {
      setErrors((prev) => ({ ...prev, dp_type: undefined }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "mobile_number" && (!/^\d*$/.test(value) || value.length > 10))
      return;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleSelectChange = (name, selectedOptions) => {
    const isMulti = ["business_entity", "data_processor"].includes(name);
    let value = [];
    if (selectedOptions) {
      value = Array.isArray(selectedOptions)
        ? selectedOptions.map((opt) => opt.value)
        : isMulti
        ? [selectedOptions.value]
        : selectedOptions.value;
    }
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (name === "category") {
      setFormData((prev) => ({ ...prev, sub_category: "" }));
    }
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const getSelectedOption = (options, value) =>
    options.find((opt) => opt.value === value) || null;

  const getSelectedOptions = (options, values) =>
    Array.isArray(values)
      ? options.filter((opt) => values.includes(opt.value))
      : [];

  const validateForm = () => {
    const newErrors = {};
    if (!formData.email.trim()) newErrors.email = "Email is required";
    else if (!/^[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}$/.test(formData.email))
      newErrors.email = "Enter a valid email";
    if (!formData.mobile_number.trim())
      newErrors.mobile_number = "Mobile number is required";
    else if (!/^\d{10}$/.test(formData.mobile_number))
      newErrors.mobile_number = "Enter a valid 10-digit mobile number";
    if (!formData.subject.trim()) newErrors.subject = "Subject is required";
    if (!formData.message.trim() || formData.message.trim().length < 20)
      newErrors.message = "Message must be at least 20 characters long";
    if (formData.dp_type.length === 0)
      newErrors.dp_type = "DP Type is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isFormValid = () =>
    /^[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}$/.test(formData.email) &&
    /^\d{10}$/.test(formData.mobile_number) &&
    formData.subject.trim() &&
    formData.message.trim().length >= 20 &&
    formData.dp_type.length > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      const res = await apiCall("/api/v1/grievance/raise-grievance", {
        method: "POST",
        data: {
          ...formData,
          email: formData.email.trim(),
          subject: formData.subject.trim(),
          message: formData.message.trim(),
          business_entity: formData.business_entity,
          data_processor: formData.data_processor,
        },
      });

      const grievanceId = res?.grievance_id;
      toast.success(res.message || "Request submitted successfully!");

      if (attachmentFiles && attachmentFiles.length > 0) {
        const uploadFormData = new FormData();

        attachmentFiles.forEach((file, index) => {
          uploadFormData.append("files", file);
        });

        await uploadFile(
          `/api/v1/grievance/upload-reference-document?grievance_id=${grievanceId}`,
          {
            method: "PATCH",
            data: uploadFormData,
          }
        );

        toast.success("File uploaded successfully!");
      }
      setShowModal(true);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="pt-10 h-screen w-full flex justify-center overflow-y-auto">
      <div className="w-[662px] mt-8">
        <h1 className="text-[#000000] text-[28px] font-medium">
          Raise Grievances
        </h1>
        <p className="text-subHeading text-sm">
          Provide your details and request information to help us process your
          data privacy query efficiently
        </p>

        <form
          className="mt-5 flex flex-col gap-y-3.5 pb-20"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="sm:flex sm:flex-col gap-3 mb-2">
            <p className="text-sm">
              I am<span className="text-red-400 text-lg">*</span>
            </p>
            <div className="flex flex-wrap gap-3 text-center">
              {DP_IDENTITY.map((buttonLabel, index) => (
                <div
                  key={index}
                  onClick={() => handleButtonClick(buttonLabel)}
                  className={`flex justify-center items-center cursor-pointer text-sm gap-2 rounded-full text-center px-4 py-1 border border-[#1D478E] ${
                    clickedButtons.includes(buttonLabel)
                      ? "bg-[#1D478E] text-white"
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
            {errors.dp_type && (
              <p className="text-red-500 text-xs mt-1">{errors.dp_type}</p>
            )}
          </div>

          <div className="flex gap-6 ">
            <div className="w-1/2">
              <InputField
                label="Email"
                name="email"
                type="email"
                placeholder="Enter Your Email"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                tooltipText="Used to send confirmation and status updates regarding your request."
                required
                className="bg-transparent"
              />
            </div>
            <div className="w-1/2">
              <InputField
                label="Mobile Number"
                name="mobile_number"
                placeholder={"Enter Your Mobile Number"}
                type="tel"
                value={formData.mobile_number}
                onChange={handleChange}
                error={errors.mobile_number}
                tooltipText="Helps us contact you if additional verification is required."
                className="bg-transparent"
              />
            </div>
          </div>
          <div className="flex gap-6">
            <div className="w-1/2">
              <SelectInput
                label="Category"
                options={CATEGORY_OPTIONS}
                value={getSelectedOption(CATEGORY_OPTIONS, formData.category)}
                onChange={(sel) => handleSelectChange("category", sel)}
                enableCustomOption={true}
                customOptionLabel="Other Category"
                className="bg-transparent"
                tooltipText="Helps in assigning your request to the right team."
                placeholder="Select category"
              />
            </div>
            <div className="w-1/2">
              <SelectInput
                label="Sub-Category"
                options={availableSubCategories}
                value={getSelectedOption(
                  availableSubCategories,
                  formData.sub_category
                )}
                onChange={(sel) => handleSelectChange("sub_category", sel)}
                isDisabled={!formData.category}
                enableCustomOption={true}
                customOptionLabel="Other (specify)"
                tooltipText="Helps in assigning your request to the right team."
                className="bg-transparent"
                placeholder="Select sub-category"
              />
            </div>
          </div>
          <InputField
            label="Subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            error={errors.subject}
            required
            placeholder="Write the subject here"
            tooltipText="Helps categorize and identify your request quickly."
            className="bg-transparent"
          />
          <TextareaField
            label="Message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            error={errors.message}
            rows={5}
            required
            placeholder="Write your message here ( minimum 20 characters )"
            tooltipText="Include relevant details to ensure faster resolution."
            className="bg-transparent"
          />

          <div>
            <h2 className="text-sm font-medium">Supporting Documents</h2>
            <FileUpload
              title="Attachments"
              multiple
              onFileSelect={(files) => setAttachmentFiles(files)}
            />
          </div>

          <div className="flex justify-end gap-2  py-4">
            <Button variant="cancel" type="button">
              Cancel
            </Button>
            <Button
              variant={isFormValid() ? "primary" : "ghost"}
              type="submit"
              disabled={!isFormValid() || isSubmitting}
            >
              {isSubmitting ? "Submitting..." : "Submit"}
            </Button>
          </div>
        </form>
        <Modal
          isOpen={showModal}
          title="Check Mail"
          message="We've sent a verification link to your email."
          onConfirm={() => {
            setShowModal(false);
          }}
          onClose={() => {
            setShowModal(false);
            router.push("/raise-grievance");
          }}
        />
      </div>
    </div>
  );
};

export default Page;
