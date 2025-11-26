"use client";

import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";

const WebhookCreationDetailsModal = ({ isOpen, onClose, webhookDetails }) => {
  if (!isOpen || !webhookDetails) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Webhook Created Successfully!">
      <div className="flex flex-col gap-4">
        <p className="text-lg font-semibold text-green-600">Your webhook has been created.</p>
        <p className="text-sm text-gray-700">Please save the following details, especially the Secret Token, as it will not be shown again.</p>
        <InputField label="Webhook ID" value={webhookDetails.webhook_id} readOnly />
        <InputField label="Secret Token" value={webhookDetails.secret_token} readOnly />
        <div className="flex justify-end mt-4">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </Modal>
  );
};

export default WebhookCreationDetailsModal;
