"use client";

import { useState, useEffect } from "react";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import CheckboxGroup from "@/components/ui/CheckboxGroup";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

const CONSENT_EVENT_OPTIONS = [
  { value: "CONSENT_GRANTED", label: "Consent Granted" },
  { value: "CONSENT_VALIDATED", label: "Consent Validated" },
  { value: "CONSENT_UPDATED", label: "Consent Updated" },
  { value: "CONSENT_RENEWED", label: "Consent Renewed" },
  { value: "CONSENT_WITHDRAWN", label: "Consent Withdrawn" },
  { value: "CONSENT_EXPIRED", label: "Consent Expired" },
  {
    value: "DATA_ERASURE_MANUAL_TRIGGERED",
    label: "Data Erasure Manual Triggered",
  },
  {
    value: "DATA_ERASURE_RETENTION_TRIGGERED",
    label: "Data Erasure Retention Triggered",
  },
  { value: "DATA_UPDATE_REQUESTED", label: "Data Update Requested" },
  { value: "GRIEVANCE_RAISED", label: "Grievance Raised" },
];

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
  const [dprs, setDprs] = useState([]);
  const [selectedEvents, setSelectedEvents] = useState([]);

  useEffect(() => {
    if (editingWebhook) {
      setFormData({
        url: editingWebhook.url || "",
        webhook_for: editingWebhook.webhook_for || "df",
        dpr_id: editingWebhook.dpr_id || "",
        environment: editingWebhook.environment || "testing",
      });
      setSelectedEvents(
        editingWebhook.subscribed_events ||
          CONSENT_EVENT_OPTIONS.map((event) => event.value)
      );
    } else {
      setSelectedEvents(CONSENT_EVENT_OPTIONS.map((event) => event.value));
    }
  }, [editingWebhook]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (selectedValues) => {
    setSelectedEvents(selectedValues);
  };

  const handleSelectAllChange = (e) => {
    if (e.target.checked) {
      setSelectedEvents(CONSENT_EVENT_OPTIONS.map((event) => event.value));
    } else {
      setSelectedEvents([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const dataToSend = { ...formData, subscribed_events: selectedEvents };
      if (editingWebhook) {
        await apiCall(`/webhooks/update-webhook/${editingWebhook.webhook_id}`, {
          method: "PUT",
          data: dataToSend,
        });
        toast.success("Webhook updated successfully");
      } else {
        const response = await apiCall("/webhooks/create-webhook", {
          method: "POST",
          data: dataToSend,
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

  const getAllVendors = async () => {
    try {
      const response = await apiCall("/vendor/get-all-vendors");
      setDprs(response.vendors || []);
    } catch (error) {
      const message = getErrorMessage(error);
      console.error(error);
    }
  };

  useEffect(() => {
    getAllVendors();
  }, []);

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
          isClearable={false}
        />

        {formData.webhook_for === "dpr" && (
          <SelectInput
            label="Data Processor"
            name="dpr_id"
            value={dprs.find((dpr) => dpr.dpr_id === formData.dpr_id)}
            onChange={(selectedOption) =>
              handleSelectChange("dpr_id", selectedOption.value)
            }
            options={dprs.map((dpr) => ({
              value: dpr._id,
              label: dpr.dpr_name,
            }))}
            placeholder="Select Data Processor"
            isClearable={false}
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
          isClearable={false}
        />

        <CheckboxGroup
          label="Subscribed Events"
          options={CONSENT_EVENT_OPTIONS}
          selectedValues={selectedEvents}
          onChange={handleCheckboxChange}
          selectAllCheckbox={true}
          isAllSelected={selectedEvents.length === CONSENT_EVENT_OPTIONS.length}
          onSelectAllChange={handleSelectAllChange}
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
