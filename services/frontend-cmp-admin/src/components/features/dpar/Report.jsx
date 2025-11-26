import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import Button from "@/components/ui/Button";
import { apiCall } from "@/hooks/apiCall";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useEffect } from "react";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

const typeOptions = [
  { label: "Message", value: "message" },
  { label: "Completion", value: "completion" },
  { label: "Acknowledgement", value: "acknowledgement" },
  { label: "Request", value: "request" },
  { label: "Rejection", value: "rejection" },
];

const templateOptions = [
  { label: "Template 01", value: "one" },
  { label: "Template 02", value: "two" },
  { label: "Template 03", value: "three" },
];

const Report = ({ data, fetchData, onReportSent, loading }) => {
  const router = useRouter();
  const [coreIdentifier, setCoreIdentifier] = useState(false);
  const [secondaryIdentifier, setSecondaryIdentifier] = useState(false);
  const [type, setType] = useState(null);
  const [template, setTemplate] = useState(null);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleTypeChange = (selectedOption) => {
    setType(selectedOption);
  };

  const handleTemplateChange = (selectedOption) => {
    setTemplate(selectedOption);
  };

  useEffect(() => {
    if (data) {
      const hasCore =
        !!data.core_identifier && data.core_identifier.trim() !== "";
      setCoreIdentifier(hasCore);

      const hasSecondary =
        !!data.secondary_identifier && data.secondary_identifier.trim() !== "";
      setSecondaryIdentifier(hasSecondary);
    }
  }, [data]);

  const validateForm = () => {
    const newErrors = {};

    if (!type) {
      newErrors.type = "Type is required";
    }

    if (!template) {
      newErrors.template = "Template is required";
    }

    if (type && ["message", "request", "rejection"].includes(type.value)) {
      if (!subject.trim()) {
        newErrors.subject = "Subject is required";
      }
      if (!message.trim()) {
        newErrors.message = "Message is required";
      }
    }

    if (!coreIdentifier && !secondaryIdentifier) {
      newErrors.recipients = "At least one recipient must be selected";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});
    setSuccessMessage("");

    if (!data?._id) {
      setErrors({ apiError: "Missing request ID" });
      setIsSubmitting(false);
      return;
    }

    if (!validateForm()) {
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = {
        report_type: type.value,
        template_id: template.value,
        send_to:
          coreIdentifier && secondaryIdentifier
            ? "core"
            : coreIdentifier
            ? "core"
            : "secondary",
        subject: subject,
        message: message,
      };

      const response = await apiCall(
        `/dpar/send-report?request_id=${data._id}`,
        {
          method: "POST",
          data: payload,
        }
      );
      router.push(`/user/dpar/incoming/${data._id}?activeTab=message`);

      setType(null);
      setTemplate(null);
      setSubject("");
      setMessage("");
      setSuccessMessage("");
      fetchData();
      onReportSent();

      toast.success("Report sent successfully!");
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const hasCoreValue =
    data?.core_identifier && data.core_identifier.trim() !== "";
  const hasSecondaryValue =
    data?.secondary_identifier && data.secondary_identifier.trim() !== "";

  return (
    <div className="pt-6 px-6  h-[calc(100vh-176px)] overflow-y-auto  custom-scrollbar">
      <div className="container mx-auto max-w-xl px-6">
        <h1 className="text-[22px] font-semibold text-heading">Report</h1>
        <p className="text-xs font-light text-subHeading">
          Add basic details about the incident, like what happened, its type,
          and who is handling it.
        </p>
      </div>

      <div className="container mx-auto max-w-xl p-6">
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Email Sent To
            </label>
            <div className="flex gap-4">
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  className="form-checkbox accent-blue-500"
                  checked={hasCoreValue ? coreIdentifier : false}
                  onChange={(e) =>
                    hasCoreValue && setCoreIdentifier(e.target.checked)
                  }
                  disabled={!hasCoreValue}
                />
                <span
                  className={`ml-2 text-sm ${
                    !hasCoreValue ? "text-gray-400" : ""
                  }`}
                >
                  Core Identifier {!hasCoreValue && "(Not available)"}
                </span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  className="form-checkbox accent-blue-500"
                  checked={hasSecondaryValue ? secondaryIdentifier : false}
                  onChange={(e) =>
                    hasSecondaryValue &&
                    setSecondaryIdentifier(e.target.checked)
                  }
                  disabled={!hasSecondaryValue}
                />
                <span
                  className={`ml-2 text-sm ${
                    !hasSecondaryValue ? "text-gray-400" : ""
                  }`}
                >
                  Secondary Identifier {!hasSecondaryValue && "(Not available)"}
                </span>
              </label>
            </div>
          </div>

          <div>
            <SelectInput
              label="Type"
              options={typeOptions}
              value={type}
              onChange={handleTypeChange}
              placeholder="Select Type"
              error={errors.type}
            />
          </div>

          <div>
            <SelectInput
              label="Template"
              options={templateOptions}
              value={template}
              onChange={handleTemplateChange}
              placeholder="Select Template"
              error={errors.template}
            />
          </div>

          <div>
            <InputField
              label="Subject"
              placeholder="Write Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required={
                type && ["message", "request", "rejection"].includes(type.value)
              }
              error={errors.subject}
            />
          </div>

          <div>
            <TextareaField
              label="Message"
              placeholder="Write a Message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required={
                type && ["message", "request", "rejection"].includes(type.value)
              }
              error={errors.message}
            />
          </div>

          {errors.apiError && (
            <div className="text-sm text-red-600">{errors.apiError}</div>
          )}

          {successMessage && (
            <div className="text-sm text-green-600">{successMessage}</div>
          )}

          <div className="flex justify-end">
            <Button
              variant="primary"
              type="submit"
              className="px-4 py-2 text-white"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Sending..." : "Send"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Report;
