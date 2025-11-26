"use client";

import { useState, useEffect } from "react";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

const WEBHOOK_FOR_OPTIONS = [
  { value: "df", label: "Data Fiduciary" },
  { value: "dpr", label: "Data Processor" },
];

const ENVIRONMENT_OPTIONS = [
  { value: "testing", label: "Testing" },
  { value: "production", label: "Production" },
];

const AddEditWebhookModal = ({
  closeModal,
  fetchWebhooks,
  editingWebhook,
  onWebhookCreated,
}) => {
  const [formData, setFormData] = useState({
    url: "",
    webhook_for: "df",
    dpr_id: "",
    environment: "testing",
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingWebhook) {
      setFormData({
        url: editingWebhook.url || "",
        webhook_for: editingWebhook.webhook_for || "df",
        dpr_id: editingWebhook.dpr_id || "",
        environment: editingWebhook.environment || "testing",
      });
    }
  }, [editingWebhook]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingWebhook) {
        await apiCall(`/webhooks/update-webhook/${editingWebhook.webhook_id}`, {
          method: "PUT",
          data: formData,
        });
        toast.success("Webhook updated successfully");
      } else {
        const response = await apiCall("/webhooks/create-webhook", {
          method: "POST",
          data: formData,
        });
        toast.success(response.message || "Webhook created successfully");
        if (onWebhookCreated) {
          onWebhookCreated(response);
        }
      }
      fetchWebhooks();
      closeModal();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={closeModal}
      title={editingWebhook ? "Edit Webhook" : "Add New Webhook"}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <InputField
          label="Webhook URL"
          name="url"
          value={formData.url}
          onChange={handleChange}
          placeholder="https://example.com/webhook"
          required
        />

        <SelectInput
          label="Webhook For"
          name="webhook_for"
          value={WEBHOOK_FOR_OPTIONS.find(
            (option) => option.value === formData.webhook_for
          )}
          onChange={(selectedOption) =>
            handleSelectChange("webhook_for", selectedOption.value)
          }
          options={WEBHOOK_FOR_OPTIONS}
        />

        {formData.webhook_for === "dpr" && (
          <InputField
            label="DPR ID"
            name="dpr_id"
            value={formData.dpr_id}
            onChange={handleChange}
            placeholder="Enter DPR ID"
            required
          />
        )}

        <SelectInput
          label="Environment"
          name="environment"
          value={ENVIRONMENT_OPTIONS.find(
            (option) => option.value === formData.environment
          )}
          onChange={(selectedOption) =>
            handleSelectChange("environment", selectedOption.value)
          }
          options={ENVIRONMENT_OPTIONS}
        />

        <div className="flex justify-end gap-2 mt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={closeModal}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading
              ? "Saving..."
              : editingWebhook
              ? "Update Webhook"
              : "Add Webhook"}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default AddEditWebhookModal;
