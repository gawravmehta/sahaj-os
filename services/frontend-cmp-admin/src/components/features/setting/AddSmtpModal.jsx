"use client";

import Button from "@/components/ui/Button";
import { CreatableInputs, InputField } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useState } from "react";
import toast from "react-hot-toast";
import { RxCross2 } from "react-icons/rx";

function AddSmtpModal({ closeModal, fetchData }) {
  const [FormData, setFormData] = useState({
    df_smtp_provider: "",
    df_smtp_host: "",
    df_smtp_port: 25,
    df_smtp_username: "",
    df_smtp_tls: true,
    df_smtp_from_email: "",
    df_smtp_from_name: "",
  });

  const [missingFields, setMissingFields] = useState("");

  const handleSubmit = async () => {
    try {
      const response = await apiCall(`/smtp`, {
        method: "POST",
        data: FormData,
      });

      toast.success(response.message);
      closeModal();
      fetchData();
    } catch (error) {
      const message = getErrorMessage(error);

      toast.error(message);
    }
  };

  const portOptions = [
    { value: "465", label: "465" },
    { value: "587", label: "587" },
    { value: "25", label: "25" },
    { value: "2525", label: "2525" },
  ];
  return (
    <div
      onClick={closeModal}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex w-[500px] flex-col justify-between border border-[#c7cfe2] bg-white p-6"
      >
        <div>
          <Button variant="close" className="flex w-full justify-end">
            <RxCross2 onClick={closeModal} size={20} />
          </Button>
          <h2 className="text-xl font-semibold">Add SMTP</h2>
          <p className="mb-4 mt-2 text-xs text-gray-400 ">
            Provide detailed information about the data element to ensure
            accurate categorization and usage.
          </p>
          <div className="space-y-4 h-[60vh] overflow-y-auto custom-nav-scrollbar pr-4 pb-4">
            <InputField
              name={"SMTP Provider"}
              label="SMTP Provider"
              placeholder="Enter SMTP Provider"
              value={FormData.df_smtp_provider}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_provider: e.target.value,
                }))
              }
              required={true}
            />
            <InputField
              name={"Host"}
              label="Host"
              placeholder="Enter Host"
              value={FormData.df_smtp_host}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_host: e.target.value,
                }))
              }
              required={true}
            />
            <CreatableInputs
              name={"SMTP Port"}
              label="SMTP Port"
              placeholder="Enter SMTP Port"
              options={portOptions}
              value={
                FormData.df_smtp_port
                  ? {
                      value: FormData.df_smtp_port,
                      label: FormData.df_smtp_port,
                    }
                  : null
              }
              onChange={(selected) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_port: selected?.value || "",
                }))
              }
              required={true}
            />
            <InputField
              name={"Username"}
              label="Username"
              placeholder="Enter SMTP Username"
              value={FormData.df_smtp_username}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_username: e.target.value,
                }))
              }
              missingFields={missingFields}
            />

            <InputField
              name={"SMTP Email"}
              label="SMTP Email"
              placeholder="Enter your smtp email"
              value={FormData.df_smtp_from_email}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_from_email: e.target.value,
                }))
              }
              required={true}
            />
            <InputField
              name={"SMTP Name"}
              label="SMTP Name"
              placeholder="Enter SMTP Name "
              value={FormData.df_smtp_from_name}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_from_name: e.target.value,
                }))
              }
            />

            <YesNoToggle
              name="df_tls"
              label="TLS"
              value={FormData.df_smtp_tls}
              onChange={() =>
                setFormData((prev) => ({
                  ...prev,
                  df_smtp_tls: !prev.df_smtp_tls,
                }))
              }
              required={true}
              tooltipText="Enable or disable TLS encryption"
              tooltipWidth="120"
            />
          </div>
        </div>
        <div className="mt-3 flex justify-end gap-3">
          <Button variant="cancel" onClick={closeModal}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={() => handleSubmit()}
            className="px-3.5"
          >
            Add
          </Button>
        </div>
      </div>
    </div>
  );
}

export default AddSmtpModal;
